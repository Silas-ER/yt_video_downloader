# YT Video Downloader

Aplicação web para baixar vídeos do YouTube de forma simples e rápida, com acompanhamento de progresso em tempo real e opção de escolher a qualidade do vídeo ou baixar apenas o áudio.

🔗 **Acesse online:** [yt-video-downloader-400e.onrender.com](https://yt-video-downloader-400e.onrender.com/)

> ⚠️ O projeto está hospedado no plano gratuito do Render, então o serviço pode hibernar após alguns minutos sem uso. O primeiro acesso após um período de inatividade pode demorar de 30 a 50 segundos para carregar.

## ✨ Funcionalidades

- Busca de informações do vídeo (título, autor, thumbnail) antes do download
- Seleção de qualidade do vídeo (múltiplas resoluções disponíveis)
- Opção de baixar somente o áudio
- Barra de progresso em tempo real durante o download
- Feedback visual de download concluído com sucesso
- Página "Sobre" com informações do projeto e área de doações

## 🛠️ Tecnologias utilizadas

- **Backend:** Python + Flask
- **Download dos vídeos:** [pytubefix](https://github.com/JuanBindez/pytubefix)
- **Frontend:** HTML + Tailwind CSS + JavaScript (sem frameworks, sem build step)
- **Deploy:** Render

## 🚀 Como rodar localmente

1. Clone o repositório:
   ```bash
   git clone https://github.com/Silas-ER/yt_video_downloader.git
   cd yt_video_downloader
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/Scripts/activate   # Windows (Git Bash)
   # ou
   source venv/bin/activate       # Linux/Mac
   ```

3. Instale as dependências:
   ```bash
   python -m pip install -r requirements.txt
   ```

4. Crie um arquivo `.env` na raiz do projeto com:
   ```
   SECRET_KEY=sua-chave-secreta-aqui
   ```

5. Rode a aplicação:
   ```bash
   python app.py
   ```

6. Acesse `http://localhost:5000` no navegador.

## 📂 Estrutura do projeto

```
yt_video_downloader/
├── static/
│   ├── images/        # favicon, qr code de doação
│   └── js/
│       └── app.js     # lógica de busca, download e progresso
├── templates/
│   ├── base.html       # layout compartilhado (header/footer)
│   ├── index.html      # página inicial - download
│   └── sobre.html       # página sobre / doações
├── app.py               # backend Flask
└── requirements.txt
```

## 💖 Apoie o projeto

Se este projeto te ajudou, considere fazer uma doação através da página [Sobre](https://yt-video-downloader-400e.onrender.com/sobre) do site.

## 👤 Autor

Desenvolvido por [Silas](https://github.com/Silas-ER).