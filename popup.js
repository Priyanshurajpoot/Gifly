document.addEventListener('DOMContentLoaded', () => {
    const audio = document.getElementById('audio-player');
    const playPauseBtn = document.getElementById('play-pause');
    const prevBtn = document.getElementById('prev');
    const nextBtn = document.getElementById('next');
    const seekSlider = document.getElementById('seek');
    const volumeSlider = document.getElementById('volume');
    const currentTime = document.getElementById('current-time');
    const duration = document.getElementById('duration');
    const seekHearts = document.getElementById('seek-hearts');
    const volumeHearts = document.getElementById('volume-hearts');
    const songList = document.getElementById('song-list');
    const funnyGif = document.getElementById('funny-gif');
    const currentIndexSpan = document.getElementById('current-index');
    const totalSongsSpan = document.getElementById('total-songs');
    const loadSongsBtn = document.getElementById('load-songs');
    const songInput = document.getElementById('song-input');
    const showSongListBtn = document.getElementById('show-song-list');
    const closeAppBtn = document.getElementById('close-app');
  
    let playlist = [];
    let currentIndex = 0;
    const seekHeartCount = 7; // As in your image
    const volumeHeartCount = 5; // As in your image
  
    // Create hearts
    const createHearts = (container, count) => {
      for (let i = 0; i < count; i++) {
        const heart = document.createElement('span');
        heart.classList.add('heart', 'empty');
        heart.textContent = '♡';
        container.appendChild(heart);
      }
    };
  
    createHearts(seekHearts, seekHeartCount);
    createHearts(volumeHearts, volumeHeartCount);
  
    // Update seek hearts
    const updateSeekHearts = (progress) => { // progress 0-100
      const filledCount = Math.round((progress / 100) * seekHeartCount);
      Array.from(seekHearts.children).forEach((heart, idx) => {
        heart.textContent = idx < filledCount ? '♥' : '♡';
        heart.classList.toggle('filled', idx < filledCount);
      });
    };
  
    // Update volume hearts
    const updateVolumeHearts = (vol) => { // vol 0-1
      const filledCount = Math.round(vol * volumeHeartCount);
      Array.from(volumeHearts.children).forEach((heart, idx) => {
        heart.textContent = idx < filledCount ? '♥' : '♡';
        heart.classList.toggle('filled', idx < filledCount);
      });
    };
  
    // Format time
    const formatTime = (seconds) => {
      const min = Math.floor(seconds / 60);
      const sec = Math.floor(seconds % 60);
      return `${min < 10 ? '0' : ''}${min}:${sec < 10 ? '0' : ''}${sec}`;
    };
  
    // Change funny GIF
    const changeGif = () => {
      const gifNum = Math.floor(Math.random() * 13) + 1;
      funnyGif.src = `imgs/${gifNum}.gif`;
    };
  
    // Load song
    const loadSong = (index) => {
      if (index < 0 || index >= playlist.length) return;
      currentIndex = index;
      audio.src = playlist[index].url;
      audio.play();
      playPauseBtn.textContent = '⏸';
      currentIndexSpan.textContent = index + 1;
      changeGif();
      updateSongList();
    };
  
    // Update song list
    const updateSongList = () => {
      songList.innerHTML = '';
      playlist.forEach((song, idx) => {
        const li = document.createElement('li');
        li.textContent = song.name;
        if (idx === currentIndex) li.style.fontWeight = 'bold';
        li.addEventListener('click', () => loadSong(idx));
        songList.appendChild(li);
      });
      totalSongsSpan.textContent = playlist.length;
    };
  
    // Load songs
    loadSongsBtn.addEventListener('click', () => {
      const files = songInput.files;
      if (files.length === 0) return;
      playlist = Array.from(files).map(file => ({
        name: file.name,
        url: URL.createObjectURL(file)
      }));
      updateSongList();
      loadSong(0);
    });
  
    // Play/Pause
    playPauseBtn.addEventListener('click', () => {
      if (audio.paused) {
        audio.play();
        playPauseBtn.textContent = '⏸';
      } else {
        audio.pause();
        playPauseBtn.textContent = '▶';
      }
    });

    // Update progress CSS variable for the blue line
    const progress = (audio.currentTime / audio.duration) * 100 || 0;
    seekSlider.style.setProperty('--progress', progress + '%');
  
    // Next/Prev
    nextBtn.addEventListener('click', () => loadSong(currentIndex + 1));
    prevBtn.addEventListener('click', () => loadSong(currentIndex - 1));
  
    // Auto-next
    audio.addEventListener('ended', () => loadSong(currentIndex + 1));
  
    // Time update
    audio.addEventListener('timeupdate', () => {
      const progress = (audio.currentTime / audio.duration) * 100 || 0;
      seekSlider.value = progress;
      updateSeekHearts(progress);
      currentTime.textContent = formatTime(audio.currentTime);
      duration.textContent = formatTime(audio.duration);
    });
  
    // Loaded metadata for duration
    audio.addEventListener('loadedmetadata', () => {
      duration.textContent = formatTime(audio.duration);
    });
  
    // Seek
    seekSlider.addEventListener('input', () => {
      const progress = seekSlider.value;
      updateSeekHearts(progress);
      audio.currentTime = (progress / 100) * audio.duration;
    });
  
    // Volume
    volumeSlider.addEventListener('input', () => {
      audio.volume = volumeSlider.value;
      updateVolumeHearts(audio.volume);
    });
    updateVolumeHearts(1); // Initial
  
    // Show/hide song list
    showSongListBtn.addEventListener('click', () => {
      songList.style.display = songList.style.display === 'block' ? 'none' : 'block';
    });
  
    // Close app
    closeAppBtn.addEventListener('click', () => window.close());
  });