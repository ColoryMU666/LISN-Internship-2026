import sys, struct, datetime, re

def decode_cache_policy(path):
    with open(path, "rb") as f:
        data = f.read()

    policy_len = struct.unpack_from("<Q", data, len(data) - 8)[0]
    policy_start = len(data) - 8 - policy_len
    policy = data[policy_start : policy_start + policy_len]
    data_bytes = data[:policy_start]

    print("=" * 60)
    print("STRUCTURE GÉNÉRALE")
    print("=" * 60)
    print(f"  data (msgpack)  : {len(data_bytes)} bytes  [0x0000 → 0x{policy_start:04x}]")
    print(f"  CachePolicy     : {policy_len} bytes  [0x{policy_start:04x} → 0x{policy_start+policy_len:04x}]")
    print(f"  taille (8B LE)  : 8 bytes")
    print(f"  total           : {len(data)} bytes")

    # --- URL ---
    # L'URL commence au début du bloc et se termine avant le premier "
    url_end = policy.find(b'"')
    url = policy[:url_end].decode("ascii")

    # --- ETag ---
    etag_start = url_end + 1
    etag_end = policy.find(b'"', etag_start)
    etag = policy[etag_start:etag_end].decode("ascii")

    print("\n" + "=" * 60)
    print("HTTP CACHE POLICY")
    print("=" * 60)
    print(f"  URL   : {url}")
    print(f"  ETag  : \"{etag}\"")

    # --- Timestamps réels (après le padding de zéros) ---
    # Le padding commence après l'ETag + \x00 et dure jusqu'aux données non-nulles
    # Les vrais timestamps sont dans la zone non-nulle après 0x0120
    print("\n" + "=" * 60)
    print("TIMESTAMPS RÉELS (zone non-nulle après padding)")
    print("=" * 60)

    TS_MIN = 0x60000000  # ~2021
    TS_MAX = 0x70000000  # ~2030
    # On ne cherche les timestamps qu'après l'offset 0x0120 (après le padding)
    search_start = 0x0120
    seen = set()
    for i in range(search_start, len(policy) - 3, 4):
        val = struct.unpack_from("<I", policy, i)[0]
        if TS_MIN <= val <= TS_MAX and val not in seen:
            seen.add(val)
            dt = datetime.datetime.fromtimestamp(val, tz=datetime.timezone.utc)
            print(f"  offset 0x{i:04x} → {val:#010x} → {dt.isoformat()}")

    # --- max-age ---
    # À offset 0x00b0+4 = 0x00b4 on voit 0x0000028b = 651 secondes ? Non,
    # cherchons les entiers 32-bit plausibles pour un max-age (1 → 365000000)
    print("\n" + "=" * 60)
    print("ENTIERS NON NULS (plausibles pour max-age, taille, flags)")
    print("=" * 60)
    search_start = url_end + len(etag) + 4  # après l'ETag et le padding immédiat
    for i in range(search_start, len(policy) - 7, 8):
        val = struct.unpack_from("<Q", policy, i)[0]
        if 0 < val < 0x2FAF080000:  # < ~200 milliards (max-age immutable = 365000000)
            print(f"  offset 0x{i:04x} → {val} (0x{val:016x})")

if __name__ == "__main__":
    decode_cache_policy(sys.argv[1])