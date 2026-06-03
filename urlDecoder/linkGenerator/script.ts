const gitInput = document.querySelector<HTMLInputElement>('input[name="git_url"]');
const branchInput = document.querySelector<HTMLInputElement>('input[name="branch"]');
const log = document.getElementById('log');
const copyLogBtn = document.getElementById('copylogbtn');

function updateLog(): void {
    const git = gitInput ? gitInput.value.trim() : '';
    const branch = branchInput ? branchInput.value.trim() : '';
    const base = `https://{{HOST['8888']}}/`;

    const params: string[] = [
        `url=https://{{HOST['8080']}}/`,
        `token={{PASSWORD}}`
    ];

    if (git) {
        params.push(`repo=${encodeURIComponent(git)}`);
    }
    if (branch) {
        params.push(`branch=${encodeURIComponent(branch)}`);
    }

    const queryString = `?${params.join('&')}`;
    const urlText = `${base}${queryString}`;

    if (log) {
        log.textContent = urlText;
    }
}

async function copyLogText(): Promise<void> {
    if (!log) {
        return;
    }

    const textToCopy = log.textContent || '';
    try {
        if (navigator.clipboard && navigator.clipboard.writeText) {
            await navigator.clipboard.writeText(textToCopy);
            return;
        }
    } catch (err) {
        console.warn('Clipboard API failed; falling back to document.execCommand', err);
    }

    const textarea = document.createElement('textarea');
    textarea.value = textToCopy;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'absolute';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
}

function showCopiedState(): void {
    if (!copyLogBtn) {
        return;
    }

    const originalText = copyLogBtn.textContent;
    copyLogBtn.textContent = 'Copied!';
    copyLogBtn.classList.add('copied');
    copyLogBtn.disabled = true;

    window.setTimeout(() => {
        copyLogBtn.textContent = originalText;
        copyLogBtn.classList.remove('copied');
        copyLogBtn.disabled = false;
    }, 1500);
}

if (copyLogBtn) {
    copyLogBtn.addEventListener('click', async () => {
        await copyLogText();
        showCopiedState();
    });
}

if (gitInput) {
    gitInput.addEventListener('input', updateLog);
}
if (branchInput) {
    branchInput.addEventListener('input', updateLog);
}

updateLog();
