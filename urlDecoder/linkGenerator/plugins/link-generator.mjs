function render({ model, el }) {
  // Inject styles into Shadow DOM
  const style = document.createElement('style');
  style.textContent = `
    .lg-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 24px;
        box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
        padding: 32px;
        max-width: 100%;
        margin: 0;
        font-family: Inter, Arial, sans-serif;
        color: #111827;
    }
    .lg-card h2 {
        margin: 0 0 8px;
        font-size: clamp(1.9rem, 2.5vw, 2.4rem);
        font-weight: 700;
    }
    .lg-description {
        margin: 0 0 24px;
        color: #475569;
        line-height: 1.6;
    }
    .lg-output-section {
        margin: 24px 0;
    }
    .lg-link-form {
        display: grid;
        gap: 24px;
    }
    .lg-repo-group {
        display: grid;
        gap: 10px;
        padding: 16px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
    }
    .lg-validated-input {
        position: relative;
    }
    .lg-validated-input input {
        padding-right: 42px;
    }
    .lg-validated-input::after {
        position: absolute;
        right: 14px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.12rem;
        pointer-events: none;
        color: transparent;
        content: '';
    }
    .lg-validated-input.valid input { border-color: #16a34a; }
    .lg-validated-input.valid::after { color: #16a34a; content: '✓'; }
    .lg-validated-input.invalid input { border-color: #dc2626; }
    .lg-validated-input.invalid::after { color: #dc2626; content: '⚠'; }
    label {
        display: block;
        font-size: 0.95rem;
        color: #334155;
        margin-bottom: 6px;
    }
    input {
        width: 100%;
        padding: 14px 16px;
        border: 1px solid #cbd5e1;
        border-radius: 14px;
        font-size: 1rem;
        background: #ffffff;
        color: #0f172a;
        box-sizing: border-box;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    input::placeholder { color: #94a3b8; }
    input:focus {
        outline: none;
        border-color: #6366f1;
        box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.12);
    }
    .lg-branch-note {
        font-size: 0.85rem;
        color: #64748b;
        margin-top: -6px;
        margin-bottom: 12px;
        line-height: 1.4;
    }
    .lg-branch-highlight { color: #0f172a; font-weight: 700; }
    .lg-output-panel { display: grid; gap: 10px; flex: 1; }
    .lg-output-label {
        font-size: 0.92rem;
        color: #475569;
        margin-bottom: 10px;
        width: 100%;
    }
    .lg-output-row {
        display: flex;
        align-items: center;
        border: 1px solid #cbd5e1;
        border-radius: 16px;
        background: #eef2ff;
        padding: 4px 4px 4px 16px;
        gap: 8px;
    }
    #lg-log {
        flex: 1;
        margin: 0;
        padding: 10px 0;
        border: none;
        border-radius: 0;
        background: transparent;
        color: #0f172a;
        white-space: pre-wrap;
        word-break: break-word;
        overflow-wrap: break-word;
        min-height: 2rem;
        line-height: 1.6;
        font-family: monospace;
    }
    #lg-copylogbtn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-height: 38px;
        padding: 0 14px;
        border: none;
        border-radius: 12px;
        background: #4f46e5;
        color: white;
        font-size: 0.9rem;
        font-weight: 600;
        cursor: pointer;
        transition: transform 0.2s ease, background-color 0.2s ease;
        flex-shrink: 0;
    }
    #lg-copylogbtn:hover { background: #4338ca; transform: translateY(-1px); }
    #lg-copylogbtn:focus-visible {
        outline: 3px solid rgba(99, 102, 241, 0.35);
        outline-offset: 3px;
    }
    #lg-copylogbtn.copied {
        background: #16a34a;
        box-shadow: 0 10px 25px rgba(22, 163, 74, 0.18);
    }
    #lg-copylogbtn.copied:hover { background: #15803d; }
    .lg-app-section {
        display: grid;
        gap: 10px;
    }
    .lg-app-options {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }
    .lg-app-btn {
        padding: 10px 20px;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        background: white;
        color: #334155;
        font-size: 0.95rem;
        font-weight: 500;
        cursor: pointer;
        transition: border-color 0.2s ease, background 0.2s ease, color 0.2s ease;
    }
    .lg-app-btn:hover {
        border-color: #6366f1;
        color: #4f46e5;
    }
    .lg-app-btn.selected {
        border-color: #4f46e5;
        background: #eef2ff;
        color: #4f46e5;
        font-weight: 600;
    }
    .lg-app-fields {
        display: grid;
        gap: 10px;
        margin-top: 12px;
    }
    .lg-app-field-wrapper {
        display: grid;
        gap: 6px;
    }
  `;
  el.appendChild(style);

  const container = document.createElement('div');
  container.className = 'lg-card';
  container.innerHTML = `
    <h2>Link generator</h2>
    <p class="lg-description">Generate a launcher URL from a Git repository, optional branch, and optional file path.</p>
    <div class="lg-output-section">
      <div class="lg-output-label">Generated URL</div>
      <div class="lg-output-row">
        <pre id="lg-log" aria-live="polite">URL will appear here</pre>
        <button id="lg-copylogbtn" type="button">Copy</button>
      </div>
    </div>
    <form class="lg-link-form" onsubmit="return false;" autocomplete="off">
      <div class="lg-repo-group">
        <label for="lg-git_env_url">Git Environment Repository URL</label>
        <div class="lg-validated-input" aria-live="polite">
          <input id="lg-git_env_url" name="git_env_url" placeholder="https://github.com/example/test" required>
        </div>
        <label for="lg-git_env_branch">Environment repository branch</label>
        <div class="lg-validated-input">
          <input id="lg-git_env_branch" name="git_env_branch" placeholder="main" value="main">
        </div>
        <div class="lg-branch-note">use <span class="lg-branch-highlight">master</span> instead of <span class="lg-branch-highlight">main</span> for old repositories</div>
      </div>
      <div class="lg-repo-group">
        <label for="lg-git_url">Git Content Repository URL</label>
        <div class="lg-validated-input">
          <input id="lg-git_url" name="git_url" placeholder="https://github.com/example/test">
        </div>
        <label for="lg-git_branch">Content repository branch</label>
        <div class="lg-validated-input">
          <input id="lg-git_branch" name="git_branch" placeholder="main" value="main">
        </div>
        <div class="lg-branch-note">use <span class="lg-branch-highlight">master</span> instead of <span class="lg-branch-highlight">main</span> for old repositories</div>
      </div>
      <label for="lg-file">File to open (optional)</label>
      <div class="lg-validated-input">
        <input id="lg-file" name="file" placeholder="File to open after checkout">
      </div>
    </form>
  `;
  el.appendChild(container);

  const apps = model.get('app').map(entry => Object.keys(entry)[0]);


  function renderAppSelector(apps) {
    const section = document.createElement('div');
    section.className = 'lg-app-section';
    section.innerHTML = `<div class="lg-output-label">Application</div>`;

    const optionsDiv = document.createElement('div');
    optionsDiv.className = 'lg-app-options';

    const fieldsDiv = document.createElement('div');
    fieldsDiv.className = 'lg-app-fields';

    const appData = model.get('app');

    apps.forEach((app, i) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.textContent = app;
      btn.className = 'lg-app-btn';

      btn.addEventListener('click', () => {
        optionsDiv.querySelectorAll('.lg-app-btn').forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');

        fieldsDiv.innerHTML = '';
        const fields = appData[i][app];
        fields.forEach(fieldEntry => {
          const fieldKey = Object.keys(fieldEntry)[0];
          const fieldDef = fieldEntry[fieldKey];

          const wrapper = document.createElement('div');
          wrapper.className = 'lg-app-field-wrapper';

          const label = document.createElement('label');
          label.textContent = fieldDef.title;

          const input = document.createElement('input');
          input.type = 'text';
          input.value = fieldDef.default;
          input.placeholder = fieldDef.tooltip;
          input.title = fieldDef.tooltip;
          input.dataset.key = fieldKey;

          wrapper.appendChild(label);
          wrapper.appendChild(input);
          fieldsDiv.appendChild(wrapper);
        });
      });

      optionsDiv.appendChild(btn);
    });

    section.appendChild(optionsDiv);
    section.appendChild(fieldsDiv);
    container.querySelector('.lg-link-form').appendChild(section);
  }

  renderAppSelector(apps);

  const gitEnvInput = container.querySelector('#lg-git_env_url');
  const gitEnvWrapper = gitEnvInput.closest('.lg-validated-input');
  const gitEnvBranchInput = container.querySelector('#lg-git_env_branch');
  const gitEnvBranchWrapper = gitEnvBranchInput.closest('.lg-validated-input');
  const gitInput = container.querySelector('#lg-git_url');
  const gitWrapper = gitInput.closest('.lg-validated-input');
  const gitBranchInput = container.querySelector('#lg-git_branch');
  const gitBranchWrapper = gitBranchInput.closest('.lg-validated-input');
  const fileInput = container.querySelector('#lg-file');
  const fileWrapper = fileInput.closest('.lg-validated-input');
  const log = container.querySelector('#lg-log');
  const copyLogBtn = container.querySelector('#lg-copylogbtn');

  function getRepoName(gitUrl) {
    const cleanUrl = gitUrl.replace(/\/+$/, '');
    return cleanUrl.split('/').pop() || '';
  }

  function isValidUrl(value) {
    return value.startsWith('http://') || value.startsWith('https://');
  }

  function updateFieldState(wrapper, input, alwaysValid = false) {
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
    const gitEnv = gitEnvInput.value.trim();
    const gitEnvBranch = gitEnvBranchInput.value.trim();
    const git = gitInput.value.trim();
    const branch = gitBranchInput.value.trim();
    const file = fileInput.value.trim();
    const base = `https://{{HOST['8888']}}/`;

    const gitEnvValid = gitEnv.length > 0 && isValidUrl(gitEnv);
    gitEnvWrapper.classList.remove('valid', 'invalid');
    gitEnvWrapper.classList.add(gitEnvValid ? 'valid' : 'invalid');
    gitEnvInput.setAttribute('aria-invalid', gitEnvValid ? 'false' : 'true');
    updateFieldState(gitEnvBranchWrapper, gitEnvBranchInput, true);
    const gitValid = git.length === 0 || isValidUrl(git);
    gitWrapper.classList.remove('valid', 'invalid');
    gitWrapper.classList.add(gitValid ? 'valid' : 'invalid');
    gitInput.setAttribute('aria-invalid', gitValid ? 'false' : 'true');
    updateFieldState(gitBranchWrapper, gitBranchInput, true);
    updateFieldState(fileWrapper, fileInput, true);

    const params = [
      `url=https://{{HOST['8080']}}/`,
      `token={{PASSWORD}}`
    ];
    if (gitEnv) {
      params.push(`envRepo=${encodeURIComponent(gitEnv)}`);
      if (gitEnvBranch) params.push(`envBranch=${encodeURIComponent(gitEnvBranch)}`);
    }
    if (git) {
      params.push(`ressourceRepo=${encodeURIComponent(git)}`);
      const repoName = getRepoName(git);
      if (repoName) {
        const path = file ? `lab/tree/${repoName}/${file}` : `lab/tree/${repoName}`;
        params.push(`urlPath=${encodeURIComponent(path)}`);
      }
      if (branch) params.push(`ressourceBranch=${encodeURIComponent(branch)}`);
    }

    log.textContent = `${base}?${params.join('&')}`;
  }

  async function copyLogText() {
    const textToCopy = log.textContent || '';
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(textToCopy);
        return;
      }
    } catch (err) {
      console.warn('Clipboard API failed; falling back to execCommand', err);
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

  copyLogBtn.addEventListener('click', async () => {
    await copyLogText();
    showCopiedState();
  });

  gitEnvInput.addEventListener('input', updateLog);
  gitEnvBranchInput.addEventListener('input', updateLog);
  gitInput.addEventListener('input', updateLog);
  gitBranchInput.addEventListener('input', updateLog);
  fileInput.addEventListener('input', updateLog);

  updateLog();

  return () => {
    container.remove();
    style.remove();
  };
}

export default { render };
