const gitEnvInput = document.querySelector('input[name="git_env_url"]');
const gitEnvWrapper = gitEnvInput ? gitEnvInput.closest('.validated-input') : null;
const gitEnvBranchInput = document.querySelector('input[name="git_env_branch"]');
const gitEnvBranchWrapper = gitEnvBranchInput ? gitEnvBranchInput.closest('.validated-input') : null;
const gitInput = document.querySelector('input[name="git_url"]');
const gitWrapper = gitInput ? gitInput.closest('.validated-input') : null;
const gitBranchInput = document.querySelector('input[name="git_branch"]');
const gitBranchWrapper = gitBranchInput ? gitBranchInput.closest('.validated-input') : null;
const fileInput = document.querySelector('input[name="file"]');
const fileWrapper = fileInput ? fileInput.closest('.validated-input') : null;
const log = document.getElementById('log');
const copyLogBtn = document.getElementById('copylogbtn');

function getRepoName(gitUrl) {
    const cleanUrl = gitUrl.replace(/\/+$/, '');
    return cleanUrl.split('/').pop() || '';
}

function updateValidation() {
    if (!gitEnvInput || !gitEnvWrapper) {
        return;
    }

    const value = gitEnvInput.value.trim();
    gitEnvWrapper.classList.remove('valid', 'invalid');
    if (value.length === 0) {
        gitEnvWrapper.classList.add('invalid');
        gitEnvInput.setAttribute('aria-invalid', 'true');
    } else {
        gitEnvWrapper.classList.add('valid');
        gitEnvInput.setAttribute('aria-invalid', 'false');
    }
}

function updateFieldState(wrapper, input, alwaysValid = false) {
    if (!wrapper || !input) {
        return;
    }

    wrapper.classList.remove('valid', 'invalid');
    if (alwaysValid || input.value.trim().length > 0) {
        wrapper.classList.add('valid');
        input.setAttribute('aria-invalid', 'false');
    } else {
        wrapper.classList.add('invalid');
        input.setAttribute('aria-invalid', 'true');
    }
}

function updateLog() {
    const gitEnv = gitEnvInput ? gitEnvInput.value.trim() : '';
    const gitEnvBranch = gitEnvBranchInput ? gitEnvBranchInput.value.trim() : '';
    const git = gitInput ? gitInput.value.trim() : '';
    const branch = gitBranchInput ? gitBranchInput.value.trim() : '';
    const file = fileInput ? fileInput.value.trim() : '';
    const base = `https://{{HOST['8888']}}/`;

    updateValidation();
    updateFieldState(gitEnvBranchWrapper, gitEnvBranchInput, true);
    updateFieldState(gitWrapper, gitInput, true);
    updateFieldState(gitBranchWrapper, gitBranchInput, true);
    updateFieldState(fileWrapper, fileInput, true);

    // Build query parameters - always include url and token
    const params = [
        `url=https://{{HOST['8080']}}/`,
        `token={{PASSWORD}}`
    ];
    if (gitEnv) {
        params.push(`envRepo=${encodeURIComponent(gitEnv)}`);
        if (gitEnvBranch) {
            params.push(`envBranch=${encodeURIComponent(gitEnvBranch)}`);
        }
    }
    if (git) {
        params.push(`repo=${encodeURIComponent(git)}`);
        const repoName = getRepoName(git);
        if (repoName) {
            const path = file ? `lab/tree/${repoName}/${file}` : `lab/tree/${repoName}`;
            params.push(`urlPath=${encodeURIComponent(path)}`);
        }
        if (branch) {
            params.push(`branch=${encodeURIComponent(branch)}`);
        }
    }
    
    const queryString = `?${params.join('&')}`;
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

if (gitEnvInput) gitEnvInput.addEventListener('input', updateLog);
if (gitEnvBranchInput) gitEnvBranchInput.addEventListener('input', updateLog);
if (gitInput) gitInput.addEventListener('input', updateLog);
if (gitBranchInput) gitBranchInput.addEventListener('input', updateLog);
if (fileInput) fileInput.addEventListener('input', updateLog);

// initialize display
updateValidation();
updateFieldState(gitEnvBranchWrapper, gitEnvBranchInput, true);
updateFieldState(gitWrapper, gitInput, true);
updateFieldState(gitBranchWrapper, gitBranchInput, true);
updateFieldState(fileWrapper, fileInput, true);
updateLog();