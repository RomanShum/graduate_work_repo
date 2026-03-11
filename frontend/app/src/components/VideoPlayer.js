// src/components/VideoPlayer.js
import React, { useState, useEffect, useRef, useCallback } from 'react';
import ReactPlayer from 'react-player';
import { videoAction, getVideoState } from '../api/rooms';
import socketManager from '../utils/nativeSocket';

const VideoPlayer = ({ sessionId, username }) => {
  const [videoUrl, setVideoUrl] = useState('');
  const [playing, setPlaying] = useState(false);
  const [played, setPlayed] = useState(0);
  const [seeking, setSeeking] = useState(false);
  const [urlInput, setUrlInput] = useState('');
  const [showUrlInput, setShowUrlInput] = useState(false);
  const [users, setUsers] = useState([]);

  const playerRef = useRef(null);
  const lastUpdateRef = useRef(0);
  const isRemoteActionRef = useRef(false);

  const loadVideoState = useCallback(async () => {
    try {
      const state = await getVideoState(sessionId);
      setVideoUrl(state.video_url || '');
      setPlaying(state.is_playing);
      setPlayed(state.current_time || 0);
    } catch (error) {
      console.error('Failed to load video state:', error);
    }
  }, [sessionId]);

  const handleVideoEvent = useCallback((data) => {
    console.log('Video event:', data);

    if (data.username === username) return;

    isRemoteActionRef.current = true;

    switch (data.action) {
      case 'play':
        setPlaying(true);
        break;
      case 'pause':
        setPlaying(false);
        break;
      case 'seek':
        setPlayed(data.time);
        if (playerRef.current) {
          playerRef.current.seekTo(data.time, 'seconds');
        }
        break;
      default:
        break;
    }

    setTimeout(() => {
      isRemoteActionRef.current = false;
    }, 100);
  }, [username]);

  const handleUserJoined = useCallback((data) => {
    console.log('User joined:', data);
    setUsers(prev => [...prev, data.username]);
  }, []);

  const handleUserLeft = useCallback((data) => {
    console.log('User left:', data);
    setUsers(prev => prev.filter(u => u !== data.username));
  }, []);

  useEffect(() => {
    loadVideoState();

    socketManager.on('video', handleVideoEvent);
    socketManager.on('user_joined', handleUserJoined);
    socketManager.on('user_left', handleUserLeft);

    return () => {
      socketManager.off('video', handleVideoEvent);
      socketManager.off('user_joined', handleUserJoined);
      socketManager.off('user_left', handleUserLeft);
    };
  }, [sessionId, loadVideoState, handleVideoEvent, handleUserJoined, handleUserLeft]);

  const handlePlay = async () => {
    if (isRemoteActionRef.current) return;

    setPlaying(true);
    await videoAction(sessionId, 'play', played, username);

    socketManager.send({
      type: 'video',
      action: 'play',
      time: played
    });
  };

  const handlePause = async () => {
    if (isRemoteActionRef.current) return;

    setPlaying(false);
    await videoAction(sessionId, 'pause', played, username);

    socketManager.send({
      type: 'video',
      action: 'pause',
      time: played
    });
  };

  const handleSeek = async (seconds) => {
    if (isRemoteActionRef.current) return;

    setPlayed(seconds);
    await videoAction(sessionId, 'seek', seconds, username);

    socketManager.send({
      type: 'video',
      action: 'seek',
      time: seconds
    });
  };

  const handleProgress = (state) => {
    if (!seeking) {
      setPlayed(state.playedSeconds);
    }
  };

  const handleSeekMouseDown = () => {
    setSeeking(true);
  };

  const handleSeekMouseUp = (e) => {
    setSeeking(false);
    const newTime = parseFloat(e.target.value);
    handleSeek(newTime);
  };

  const handleUrlSubmit = async () => {
    if (!urlInput) return;

    setVideoUrl(urlInput);
    setShowUrlInput(false);
    setUrlInput('');
  };

  return (
    <div className="video-player-container">
      <div className="video-header">
        <h3>🎥 Совместный просмотр</h3>
        <div className="users-online">
          👥 {users.length + 1} зрителей
        </div>
      </div>

      {!videoUrl && !showUrlInput && (
        <div className="no-video">
          <p>Видео не выбрано</p>
          <button onClick={() => setShowUrlInput(true)}>
            Вставить ссылку на видео
          </button>
        </div>
      )}

      {showUrlInput && (
        <div className="url-input">
          <input
            type="text"
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            placeholder="Вставьте ссылку на YouTube или другое видео"
          />
          <button onClick={handleUrlSubmit}>Загрузить</button>
          <button onClick={() => setShowUrlInput(false)}>Отмена</button>
        </div>
      )}

      {videoUrl && (
        <>
          <div className="player-wrapper">
            <ReactPlayer
              ref={playerRef}
              url={videoUrl}
              width="100%"
              height="100%"
              playing={playing}
              volume={0.8}
              onPlay={handlePlay}
              onPause={handlePause}
              onSeek={handleSeek}
              onProgress={handleProgress}
              config={{
                youtube: {
                  playerVars: { showinfo: 1 }
                }
              }}
            />
          </div>

          <div className="video-controls">
            <button onClick={() => setPlaying(!playing)}>
              {playing ? '⏸️ Пауза' : '▶️ Play'}
            </button>

            <input
              type="range"
              min={0}
              max={1}
              step="any"
              value={played}
              onMouseDown={handleSeekMouseDown}
              onMouseUp={handleSeekMouseUp}
              onChange={(e) => setPlayed(parseFloat(e.target.value))}
            />

            <span>
              {Math.floor(played / 60)}:
              {(played % 60).toFixed(0).padStart(2, '0')}
            </span>
          </div>
        </>
      )}
    </div>
  );
};

export default VideoPlayer;