const searchBtn = document.getElementById('search-btn');
const urlInput = document.getElementById('url-input');
const errorMsg = document.getElementById('error-msg');
const videoInfo = document.getElementById('video-info');
const videoThumb = document.getElementById('video-thumb');
const videoTitle = document.getElementById('video-title');
const videoAuthor = document.getElementById('video-author');
const qualitySelect = document.getElementById('quality-select');
const downloadBtn = document.getElementById('download-btn');
const progressWrap = document.getElementById('progress-wrap');
const progressBar = document.getElementById('progress-bar');
const progressPercent = document.getElementById('progress-percent');
const progressStatus = document.getElementById('progress-status');
const successMsg = document.getElementById('success-msg');

let currentUrl = null;
let pollInterval = null;

function showError(msg) {
  errorMsg.textContent = msg;
  errorMsg.classList.remove('hidden');
}

function hideError() {
  errorMsg.classList.add('hidden');
}

searchBtn.addEventListener('click', async () => {
  const url = urlInput.value.trim();
  hideError();
  successMsg.classList.add('hidden');
  progressWrap.classList.add('hidden');

  if (!url) {
    showError('Por favor insira uma URL válida!');
    return;
  }

  searchBtn.disabled = true;
  searchBtn.textContent = 'Buscando...';

  try {
    const res = await fetch('/api/info', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    const data = await res.json();

    if (!res.ok) {
      showError(data.error || 'Erro ao buscar informações do vídeo.');
      videoInfo.classList.add('hidden');
      return;
    }

    currentUrl = url;
    videoThumb.src = data.thumbnail;
    videoTitle.textContent = data.title;
    videoAuthor.textContent = data.author;

    qualitySelect.innerHTML = '';
    data.qualities.forEach((q) => {
      const opt = document.createElement('option');
      opt.value = q;
      opt.textContent = `Vídeo - ${q}`;
      qualitySelect.appendChild(opt);
    });
    if (data.has_audio_only) {
      const opt = document.createElement('option');
      opt.value = 'audio';
      opt.textContent = 'Somente áudio (M4A)';
      qualitySelect.appendChild(opt);
    }

    videoInfo.classList.remove('hidden');
  } catch (e) {
    showError('Erro de conexão ao buscar o vídeo.');
  } finally {
    searchBtn.disabled = false;
    searchBtn.textContent = 'Buscar';
  }
});

downloadBtn.addEventListener('click', async () => {
  if (!currentUrl) return;

  hideError();
  successMsg.classList.add('hidden');
  downloadBtn.disabled = true;
  progressWrap.classList.remove('hidden');
  progressStatus.textContent = 'Preparando download...';
  progressBar.style.width = '0%';
  progressPercent.textContent = '0%';

  try {
    const res = await fetch('/api/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: currentUrl, quality: qualitySelect.value })
    });
    const data = await res.json();

    if (!res.ok) {
      showError(data.error || 'Erro ao iniciar o download.');
      downloadBtn.disabled = false;
      progressWrap.classList.add('hidden');
      return;
    }

    pollProgress(data.job_id);
  } catch (e) {
    showError('Erro de conexão ao iniciar o download.');
    downloadBtn.disabled = false;
    progressWrap.classList.add('hidden');
  }
});

function pollProgress(jobId) {
  pollInterval = setInterval(async () => {
    try {
      const res = await fetch(`/api/progress/${jobId}`);
      const data = await res.json();

      if (data.status === 'downloading' || data.status === 'starting') {
        progressStatus.textContent = 'Baixando vídeo...';
        progressBar.style.width = `${data.progress}%`;
        progressPercent.textContent = `${data.progress}%`;
      }

      if (data.status === 'finished') {
        clearInterval(pollInterval);
        progressBar.style.width = '100%';
        progressPercent.textContent = '100%';
        progressStatus.textContent = 'Download concluído!';
        successMsg.classList.remove('hidden');
        downloadBtn.disabled = false;
        window.location.href = `/api/file/${jobId}`;
      }

      if (data.status === 'error') {
        clearInterval(pollInterval);
        progressWrap.classList.add('hidden');
        downloadBtn.disabled = false;
        showError(data.error || 'Erro durante o download.');
      }
    } catch (e) {
      clearInterval(pollInterval);
      downloadBtn.disabled = false;
      showError('Erro ao verificar progresso do download.');
    }
  }, 1000);
}