const gitInput = document.querySelector('input[name="git_url"]');
const branchInput = document.querySelector('input[name="branch"]');
const log = document.getElementById('log');
const copyLogBtn = document.getElementById('copylogbtn');
const inviteToggle = document.getElementById('inviteToggle');
const inviteInput = document.getElementById('inviteInput');

function updateLog() {
    const git = gitInput ? gitInput.value.trim() : '';
    const branch = branchInput ? branchInput.value.trim() : '';
    const defaultBeginning = 'https://{{HOST["8888"]}}/';

    // Build query parameters
    const params = [];
    if (git) params.push(`repo=${encodeURIComponent(git)}`);
    if (branch) params.push(`branch=${encodeURIComponent(branch)}`);
    const queryString = params.length > 0 ? `?${params.join('&')}` : '';

    // Determine base URL
    let base = defaultBeginning;
    if (inviteToggle && inviteToggle.checked && inviteInput && inviteInput.value.trim()) {
        // use the invitation base and append /user-redirect/
        let inviteBase = inviteInput.value.trim();
        // remove trailing slashes
        inviteBase = inviteBase.replace(/\/+$/, '');
        base = inviteBase + '/user-redirect/';
    }

    const urlText = `${base}${queryString}`;
    if (log) {
        log.textContent = urlText;
    }
}

async function copyLogText() {
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

function showCopiedState() {
    if (!copyLogBtn) {
        return;
    }

    const originalText = copyLogBtn.textContent;
    copyLogBtn.textContent = 'Copied!';
    copyLogBtn.classList.add('copied');
    copyLogBtn.disabled = true;

    setTimeout(() => {
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

if (gitInput) gitInput.addEventListener('input', updateLog);
if (branchInput) branchInput.addEventListener('input', updateLog);
if (inviteToggle) {
    inviteToggle.addEventListener('change', () => {
        if (inviteInput) {
            inviteInput.style.display = inviteToggle.checked ? 'block' : 'none';
            if (!inviteToggle.checked) inviteInput.value = '';
        }
        updateLog();
    });
}
if (inviteInput) inviteInput.addEventListener('input', updateLog);

// initialize display
updateLog();