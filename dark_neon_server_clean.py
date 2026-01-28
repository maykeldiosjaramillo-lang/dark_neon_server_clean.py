#!/usr/bin/env python3
"""
🎬 DARK NEON VIDEO SERVER - OPTIMIZED EDITION
Servidor autocontenido con interfaz terror/neón + Panel Admin
Autor: Claude | Tema: Terror Extremo
Versión: 2.0 - Optimizada y con carga de archivos
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import urllib.parse
import urllib.request
from datetime import datetime
import mimetypes
import subprocess
import requests
from bs4 import BeautifulSoup
import re
import time

# ═══════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════

PORT = int(os.environ.get('PORT', 8000))  # Puerto desde variable de entorno o 8000
MEDIA_DIR = "media"
VALID_KEYS = ["DEMO2026", "TERROR", "NEON"]  # Claves de usuario
ADMIN_KEY = "INTEGER"  # Clave de administrador
DOWNLOAD_KEY = "NOA"  # Clave para descargar
LIVEGORE_KEY = "NOA999"  # Clave para acceso Live Gore
GLOBAL_GORE_KEY = "NOA666"  # Clave para videos gore globales (streaming directo)

# Cache para Global Gore (evita scraping repetido)
GLOBAL_GORE_CACHE = {}
CACHE_DURATION = 300  # 5 minutos en segundos

# Sitios gore soportados
GORE_SITES = {
    'kaotic': 'https://www.kaotic.com',
    'documentingreality': 'https://www.documentingreality.com',
    'goregrish': 'https://www.goregrish.com',
    'theync': 'https://www.theync.com',
    'seegore': 'https://seegore.com',
    'hoodsite': 'https://hoodsite.com'
}

# Datos del video (edita esto para cambiar la info)
VIDEO_DATA = {
    "es": {
        "title": "EXPERIMENTO 47",
        "context": "En las profundidades de un laboratorio abandonado, se descubrió este material clasificado. Lo que verás a continuación no debería existir.",
        "warning": "⚠️ ADVERTENCIA: Contenido perturbador. No recomendado para menores de 18 años. Visualización bajo tu propio riesgo.",
        "duration": "15:47",
        "date": "27.01.2026",
        "classification": "NIVEL 5 - ULTRASECRETO"
    },
    "en": {
        "title": "EXPERIMENT 47",
        "context": "In the depths of an abandoned laboratory, this classified material was discovered. What you're about to see shouldn't exist.",
        "warning": "⚠️ WARNING: Disturbing content. Not recommended for those under 18. View at your own risk.",
        "duration": "15:47",
        "date": "01.27.2026",
        "classification": "LEVEL 5 - TOP SECRET"
    }
}

CURRENT_FILE = ""  # Archivo actual seleccionado

# Archivo para guardar configuración
CONFIG_FILE = "server_config.json"

# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════

def load_config():
    """Cargar configuración desde archivo"""
    global VIDEO_DATA, CURRENT_FILE, VALID_KEYS
    
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                VIDEO_DATA = config.get('video_data', VIDEO_DATA)
                CURRENT_FILE = config.get('current_file', CURRENT_FILE)
                VALID_KEYS = config.get('valid_keys', VALID_KEYS)
        except Exception as e:
            print(f"⚠️  Error cargando config: {e}")

def save_config():
    """Guardar configuración a archivo"""
    config = {
        'video_data': VIDEO_DATA,
        'current_file': CURRENT_FILE,
        'valid_keys': VALID_KEYS,
        'last_updated': datetime.now().isoformat()
    }
    
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"⚠️  Error guardando config: {e}")
        return False

def get_available_files():
    """Obtener lista de archivos multimedia disponibles"""
    files = []
    if os.path.exists(MEDIA_DIR):
        for filename in os.listdir(MEDIA_DIR):
            file_path = os.path.join(MEDIA_DIR, filename)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                size_mb = size / (1024 * 1024)
                files.append({
                    'name': filename,
                    'size': f"{size_mb:.2f} MB"
                })
    return files

# ═══════════════════════════════════════════════════════════════
# HTML EMBEBIDO - VERSIÓN OPTIMIZADA
# ═══════════════════════════════════════════════════════════════

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>⚠️ CLASSIFIED ACCESS</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --neon-blue: #00f3ff;
            --neon-red: #ff0055;
            --neon-yellow: #ffed00;
            --neon-green: #39ff14;
            --blood-red: #8b0000;
            --dark-bg: #0a0a0a;
            --darker-bg: #050505;
        }

        body {
            font-family: 'Courier New', monospace;
            background: var(--dark-bg);
            color: var(--neon-blue);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow-x: hidden;
            position: relative;
        }

        /* Efectos optimizados - menos intensivos */
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(transparent 50%, rgba(0, 243, 255, 0.05) 50%);
            background-size: 100% 4px;
            pointer-events: none;
            animation: scan 8s linear infinite;
            z-index: 1000;
        }

        @keyframes scan {
            0% { transform: translateY(0); }
            100% { transform: translateY(100vh); }
        }

        body::after {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-image: 
                linear-gradient(rgba(0, 243, 255, 0.1) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 243, 255, 0.1) 1px, transparent 1px);
            background-size: 50px 50px;
            pointer-events: none;
            z-index: 0;
            opacity: 0.4;
        }

        /* Efectos animados reducidos */
        .spider {
            position: fixed;
            font-size: 25px;
            z-index: 1001;
            animation: spiderWalk 20s linear infinite;
            filter: drop-shadow(0 0 5px var(--neon-red));
            cursor: pointer;
            will-change: transform;
        }

        @keyframes spiderWalk {
            0%, 100% { left: -50px; top: 10%; }
            50% { left: 100%; top: 15%; }
        }

        .flicker-light {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: var(--neon-red);
            opacity: 0;
            pointer-events: none;
            z-index: 998;
            animation: flicker 12s infinite;
        }

        @keyframes flicker {
            0%, 100% { opacity: 0; }
            5% { opacity: 0.03; }
            10% { opacity: 0; }
        }

        .container {
            position: relative;
            z-index: 10;
            width: 90%;
            max-width: 900px;
            background: rgba(10, 10, 10, 0.98);
            border: 2px solid var(--neon-blue);
            box-shadow: 0 0 30px rgba(0, 243, 255, 0.5);
            padding: 0;
        }

        .header {
            background: var(--darker-bg);
            border-bottom: 2px solid var(--neon-red);
            padding: 20px;
            position: relative;
        }

        .header h1 {
            font-size: 2em;
            text-align: center;
            color: var(--neon-red);
            text-shadow: 0 0 20px var(--neon-red);
            letter-spacing: 0.1em;
        }

        .lang-selector {
            position: absolute;
            top: 15px;
            right: 15px;
            display: flex;
            gap: 10px;
        }

        .lang-btn {
            background: transparent;
            border: 2px solid var(--neon-yellow);
            color: var(--neon-yellow);
            padding: 5px 12px;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            transition: all 0.3s;
        }

        .lang-btn:hover, .lang-btn.active {
            background: var(--neon-yellow);
            color: var(--dark-bg);
        }

        .sound-toggle {
            position: absolute;
            top: 15px;
            left: 15px;
            background: transparent;
            border: 2px solid var(--neon-green);
            color: var(--neon-green);
            padding: 5px 12px;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            transition: all 0.3s;
        }

        .sound-toggle:hover {
            background: var(--neon-green);
            color: var(--dark-bg);
        }

        .content {
            padding: 30px;
        }

        .loading {
            text-align: center;
            padding: 40px 20px;
        }

        .loading-spinner {
            width: 60px;
            height: 60px;
            border: 4px solid transparent;
            border-top: 4px solid var(--neon-blue);
            border-right: 4px solid var(--neon-red);
            border-radius: 50%;
            margin: 0 auto 20px;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .loading-text {
            color: var(--neon-blue);
            font-size: 1.1em;
        }

        /* Formulario de acceso */
        .access-form {
            text-align: center;
            max-width: 500px;
            margin: 0 auto;
        }

        .access-title {
            font-size: 1.8em;
            color: var(--neon-red);
            margin-bottom: 20px;
            text-shadow: 0 0 20px var(--neon-red);
            letter-spacing: 0.2em;
        }

        .access-subtitle {
            color: var(--neon-blue);
            margin-bottom: 30px;
            font-size: 0.95em;
            line-height: 1.6;
        }

        .access-input {
            width: 100%;
            background: var(--darker-bg);
            border: 2px solid var(--neon-blue);
            color: var(--neon-blue);
            padding: 15px 20px;
            font-family: 'Courier New', monospace;
            font-size: 1.1em;
            text-align: center;
            letter-spacing: 0.3em;
            transition: all 0.3s;
            text-transform: uppercase;
            margin-bottom: 20px;
        }

        .access-input:focus {
            outline: none;
            border-color: var(--neon-yellow);
            box-shadow: 0 0 20px rgba(255, 237, 0, 0.4);
        }

        .access-btn, .play-button, .download-btn {
            width: 100%;
            background: var(--darker-bg);
            border: 3px solid var(--neon-red);
            color: var(--neon-red);
            padding: 15px 30px;
            font-family: 'Courier New', monospace;
            font-size: 1.2em;
            cursor: pointer;
            letter-spacing: 0.2em;
            text-shadow: 0 0 10px var(--neon-red);
            transition: all 0.3s;
            margin-bottom: 15px;
        }

        .play-button {
            border-color: var(--neon-green);
            color: var(--neon-green);
            text-shadow: 0 0 10px var(--neon-green);
        }

        .download-btn {
            border-color: var(--neon-yellow);
            color: var(--neon-yellow);
            text-shadow: 0 0 10px var(--neon-yellow);
        }

        .access-btn:hover {
            background: var(--neon-red);
            color: var(--dark-bg);
            text-shadow: none;
        }

        .play-button:hover {
            background: var(--neon-green);
            color: var(--dark-bg);
            text-shadow: none;
        }

        .download-btn:hover {
            background: var(--neon-yellow);
            color: var(--dark-bg);
            text-shadow: none;
        }

        .error-message {
            background: rgba(255, 0, 85, 0.2);
            border: 2px solid var(--neon-red);
            color: var(--neon-red);
            padding: 15px;
            margin-top: 20px;
        }

        /* Información del video */
        .video-info {
            opacity: 0;
            animation: fadeIn 0.8s forwards;
        }

        @keyframes fadeIn {
            to { opacity: 1; }
        }

        .video-header {
            margin-bottom: 25px;
            padding-bottom: 20px;
            border-bottom: 2px solid rgba(0, 243, 255, 0.5);
        }

        .video-title {
            font-size: 1.8em;
            color: var(--neon-yellow);
            text-shadow: 0 0 20px var(--neon-yellow);
            letter-spacing: 0.1em;
            margin-bottom: 10px;
        }

        .video-meta {
            font-size: 0.85em;
            color: var(--neon-blue);
        }

        .classification {
            background: var(--neon-red);
            color: var(--dark-bg);
            padding: 5px 15px;
            display: inline-block;
            margin-bottom: 5px;
            font-weight: bold;
        }

        .video-context {
            background: rgba(0, 243, 255, 0.1);
            border-left: 3px solid var(--neon-blue);
            padding: 20px;
            margin-bottom: 20px;
            line-height: 1.6;
        }

        .warning-box {
            background: rgba(255, 0, 85, 0.1);
            border: 2px solid var(--neon-red);
            padding: 20px;
            margin-bottom: 25px;
            position: relative;
        }

        .warning-box::before {
            content: '⚠';
            position: absolute;
            top: -20px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 2em;
            background: var(--dark-bg);
            padding: 0 15px;
            color: var(--neon-red);
        }

        .warning-text {
            color: var(--neon-red);
            text-align: center;
            line-height: 1.6;
        }

        /* Panel de admin */
        .admin-section {
            margin-bottom: 25px;
        }

        .admin-section h3 {
            color: var(--neon-yellow);
            margin-bottom: 15px;
            text-shadow: 0 0 10px var(--neon-yellow);
        }

        .admin-input, .admin-textarea {
            width: 100%;
            margin: 10px 0;
            padding: 10px;
            background: var(--darker-bg);
            border: 2px solid var(--neon-blue);
            color: var(--neon-blue);
            font-family: 'Courier New', monospace;
        }

        .admin-textarea {
            min-height: 80px;
            resize: vertical;
        }

        .file-list {
            background: var(--darker-bg);
            border: 2px solid var(--neon-blue);
            padding: 15px;
            margin: 15px 0;
            max-height: 300px;
            overflow-y: auto;
        }

        .file-item {
            padding: 10px;
            margin: 5px 0;
            border: 1px solid rgba(0, 243, 255, 0.3);
            cursor: pointer;
            transition: all 0.3s;
        }

        .file-item:hover {
            background: rgba(0, 243, 255, 0.1);
            border-color: var(--neon-blue);
        }

        .file-item.selected {
            background: rgba(0, 243, 255, 0.2);
            border-color: var(--neon-green);
        }

        .status-bar {
            margin-top: 20px;
            padding: 15px;
            background: rgba(57, 255, 20, 0.1);
            border: 2px solid var(--neon-green);
            text-align: center;
            font-size: 0.9em;
        }

        .footer {
            background: var(--darker-bg);
            border-top: 2px solid rgba(0, 243, 255, 0.5);
            padding: 15px;
            text-align: center;
            color: rgba(0, 243, 255, 0.7);
            font-size: 0.85em;
        }

        /* Video player */
        .video-player {
            width: 100%;
            max-height: 500px;
            background: #000;
            margin-bottom: 20px;
        }

        /* Modal de descarga */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.9);
            z-index: 2000;
            justify-content: center;
            align-items: center;
        }

        .modal.active {
            display: flex;
        }

        .modal-content {
            background: var(--dark-bg);
            border: 3px solid var(--neon-yellow);
            padding: 30px;
            max-width: 500px;
            width: 90%;
            box-shadow: 0 0 50px var(--neon-yellow);
        }

        .modal-title {
            color: var(--neon-yellow);
            font-size: 1.5em;
            margin-bottom: 20px;
            text-align: center;
            text-shadow: 0 0 15px var(--neon-yellow);
        }

        .modal-close {
            background: transparent;
            border: 2px solid var(--neon-red);
            color: var(--neon-red);
            padding: 10px 20px;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            width: 100%;
            margin-top: 15px;
        }

        .modal-close:hover {
            background: var(--neon-red);
            color: var(--dark-bg);
        }

        /* Mobile responsive */
        @media (max-width: 768px) {
            .header h1 { font-size: 1.5em; }
            .video-title { font-size: 1.3em; }
            .lang-selector, .sound-toggle {
                position: static;
                margin: 10px auto;
                display: flex;
                justify-content: center;
            }
        }
    </style>
</head>
<body>
    <!-- Efectos reducidos -->
    <div class="spider" onclick="playScarySound()">🕷️</div>
    <div class="flicker-light"></div>

    <div class="container">
        <div class="header">
            <button class="sound-toggle" onclick="toggleSound()">
                <span id="sound-icon">🔇</span>
            </button>
            <h1>⚠️ CLASSIFIED ACCESS</h1>
            <div class="lang-selector">
                <button class="lang-btn active" onclick="changeLang('es')">ESP</button>
                <button class="lang-btn" onclick="changeLang('en')">ENG</button>
            </div>
        </div>
        
        <div class="content" id="content">
            <div class="loading">
                <div class="loading-spinner"></div>
                <div class="loading-text" data-es="INICIALIZANDO SISTEMA..." data-en="INITIALIZING SYSTEM...">
                    INICIALIZANDO SISTEMA...
                </div>
            </div>
        </div>

        <div class="footer">
            <span data-es="SERVIDOR ACTIVO | CONEXIÓN SEGURA" data-en="SERVER ACTIVE | SECURE CONNECTION">
                SERVIDOR ACTIVO | CONEXIÓN SEGURA
            </span>
        </div>
    </div>

    <!-- Modal de descarga -->
    <div class="modal" id="downloadModal">
        <div class="modal-content">
            <div class="modal-title" data-es="DESCARGA PROTEGIDA" data-en="PROTECTED DOWNLOAD">
                DESCARGA PROTEGIDA
            </div>
            <input 
                type="text" 
                class="access-input" 
                id="download-key" 
                placeholder="CÓDIGO DE DESCARGA"
                data-es-placeholder="CÓDIGO DE DESCARGA"
                data-en-placeholder="DOWNLOAD CODE"
            >
            <button class="access-btn" onclick="verifyDownload()">
                <span data-es="VERIFICAR" data-en="VERIFY">VERIFICAR</span>
            </button>
            <div id="download-error"></div>
            <button class="modal-close" onclick="closeDownloadModal()">
                <span data-es="CANCELAR" data-en="CANCEL">CANCELAR</span>
            </button>
        </div>
    </div>

    <script>
        // ═══════════════════════════════════════════════════════════════
        // CONFIGURACIÓN Y ESTADO
        // ═══════════════════════════════════════════════════════════════
        
        let currentLang = 'es';
        let soundEnabled = false;
        let accessGranted = false;
        let isAdmin = false;
        let isLiveGore = false;
        let isGlobalGore = false;
        let currentFile = '';

        // Traducciones
        const translations = {
            es: {
                accessTitle: "ACCESO RESTRINGIDO",
                accessSubtitle: "Este material está clasificado. Se requiere autorización de nivel 5 para continuar.",
                inputPlaceholder: "CÓDIGO DE ACCESO",
                accessButton: "VERIFICAR ACCESO",
                errorInvalid: "❌ ACCESO DENEGADO - Código inválido",
                errorServer: "❌ ERROR DE SERVIDOR - Intenta nuevamente",
                loadingText: "INICIALIZANDO SISTEMA...",
                playButton: "▶ REPRODUCIR CONTENIDO",
                downloadButton: "⬇ DESCARGAR ARCHIVO",
                adminPanel: "PANEL DE ADMINISTRACIÓN",
                selectFile: "Seleccionar Archivo",
                noFiles: "No hay archivos disponibles"
            },
            en: {
                accessTitle: "RESTRICTED ACCESS",
                accessSubtitle: "This material is classified. Level 5 authorization required to proceed.",
                inputPlaceholder: "ACCESS CODE",
                accessButton: "VERIFY ACCESS",
                errorInvalid: "❌ ACCESS DENIED - Invalid code",
                errorServer: "❌ SERVER ERROR - Try again",
                loadingText: "INITIALIZING SYSTEM...",
                playButton: "▶ PLAY CONTENT",
                downloadButton: "⬇ DOWNLOAD FILE",
                adminPanel: "ADMIN PANEL",
                selectFile: "Select File",
                noFiles: "No files available"
            }
        };

        // ═══════════════════════════════════════════════════════════════
        // SISTEMA DE AUDIO SIMPLIFICADO
        // ═══════════════════════════════════════════════════════════════
        
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        function playBeep(frequency = 800, duration = 100) {
            if (!soundEnabled) return;
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            oscillator.frequency.value = frequency;
            gainNode.gain.setValueAtTime(0.2, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + duration / 1000);
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + duration / 1000);
        }

        function playErrorSound() {
            if (!soundEnabled) return;
            playBeep(200, 100);
            setTimeout(() => playBeep(150, 200), 100);
        }

        function playSuccessSound() {
            if (!soundEnabled) return;
            playBeep(800, 100);
            setTimeout(() => playBeep(1000, 150), 100);
        }

        function playScarySound() {
            if (!soundEnabled) return;
            playBeep(Math.random() * 200 + 100, 300);
        }

        function toggleSound() {
            soundEnabled = !soundEnabled;
            document.getElementById('sound-icon').textContent = soundEnabled ? '🔊' : '🔇';
            if (soundEnabled) playBeep(600, 100);
        }

        // ═══════════════════════════════════════════════════════════════
        // SISTEMA DE IDIOMAS
        // ═══════════════════════════════════════════════════════════════
        
        function changeLang(lang) {
            currentLang = lang;
            playBeep(1000, 50);
            
            document.querySelectorAll('.lang-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
            
            document.querySelectorAll('[data-es]').forEach(el => {
                const attr = `data-${lang}`;
                if (el.tagName === 'INPUT') {
                    el.placeholder = el.getAttribute(attr + '-placeholder') || el.getAttribute(attr);
                } else {
                    el.textContent = el.getAttribute(attr);
                }
            });
            
            if (accessGranted) {
                if (isAdmin) {
                    showAdminPanel();
                } else {
                    loadVideoInfo();
                }
            } else {
                showAccessForm();
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // INTERFAZ DE ACCESO
        // ═══════════════════════════════════════════════════════════════
        
        function showAccessForm() {
            const t = translations[currentLang];
            const content = document.getElementById('content');
            
            content.innerHTML = `
                <div class="access-form">
                    <div class="access-title">${t.accessTitle}</div>
                    <div class="access-subtitle">${t.accessSubtitle}</div>
                    
                    <input 
                        type="text" 
                        class="access-input" 
                        id="access-key" 
                        placeholder="${t.inputPlaceholder}"
                        maxlength="20"
                        autocomplete="off"
                    >
                    
                    <button class="access-btn" onclick="verifyAccess()">
                        ${t.accessButton}
                    </button>
                    
                    <div id="error-container"></div>
                </div>
            `;

            document.getElementById('access-key').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') verifyAccess();
            });
        }

        // ═══════════════════════════════════════════════════════════════
        // VERIFICACIÓN DE ACCESO
        // ═══════════════════════════════════════════════════════════════
        
        async function verifyAccess() {
            const keyInput = document.getElementById('access-key');
            const key = keyInput.value.trim().toUpperCase();
            const errorContainer = document.getElementById('error-container');
            const t = translations[currentLang];
            
            if (!key) {
                playBeep(300, 200);
                return;
            }

            playBeep(1200, 100);
            errorContainer.innerHTML = '';

            try {
                const response = await fetch('/check-key', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key: key })
                });

                const result = await response.json();

                if (result.valid) {
                    playSuccessSound();
                    accessGranted = true;
                    isAdmin = result.admin || false;
                    isLiveGore = result.livegore || false;
                    isGlobalGore = result.globalgore || false;
                    
                    if (isAdmin) {
                        showAdminPanel();
                    } else if (isGlobalGore) {
                        showGlobalGorePanel();
                    } else if (isLiveGore) {
                        showLiveGorePanel();
                    } else {
                        loadVideoInfo();
                    }
                } else {
                    playErrorSound();
                    errorContainer.innerHTML = `<div class="error-message">${t.errorInvalid}</div>`;
                    keyInput.value = '';
                }
            } catch (error) {
                playErrorSound();
                errorContainer.innerHTML = `<div class="error-message">${t.errorServer}</div>`;
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // PANEL DE GLOBAL GORE (NOA666)
        // ═══════════════════════════════════════════════════════════════
        
        async function showGlobalGorePanel() {
            const content = document.getElementById('content');
            
            content.innerHTML = `
                <div class="video-info">
                    <div class="video-header">
                        <div class="video-title" style="color: var(--blood-red); text-shadow: 0 0 30px var(--blood-red);">
                            🌐 GLOBAL GORE NETWORK
                        </div>
                    </div>
                    
                    <div class="warning-box" style="border-color: var(--blood-red); background: rgba(139, 0, 0, 0.2);">
                        <div class="warning-text">
                            ⛔ CONTENIDO EXTREMO GLOBAL<br>
                            Videos en streaming directo desde sitios gore worldwide<br>
                            NO se descargan - Reproducción directa via yt-dlp<br>
                            <small>Solo mayores de 18 años - Extremadamente gráfico</small>
                        </div>
                    </div>
                    
                    <!-- Selector de sitio gore -->
                    <div style="margin-bottom: 25px; border: 2px solid var(--blood-red); padding: 20px; background: rgba(139, 0, 0, 0.1);">
                        <h3 style="color: var(--blood-red); margin-bottom: 15px; text-shadow: 0 0 15px var(--blood-red);">
                            🔴 SELECCIONAR SITIO GORE
                        </h3>
                        
                        <select class="admin-input" id="globalGoreSite" style="margin-bottom: 15px; border-color: var(--blood-red); color: var(--blood-red);">
                            <option value="">-- Selecciona un sitio --</option>
                            <option value="kaotic">🔴 Kaotic (Recomendado)</option>
                            <option value="seegore">🔴 SeeGore</option>
                            <option value="theync">🔴 TheYNC</option>
                            <option value="hoodsite">🔴 HoodSite</option>
                        </select>
                        
                        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                            <select class="admin-input" id="globalGoreFilter" style="flex: 1; border-color: var(--blood-red);">
                                <option value="recent">Más recientes</option>
                                <option value="popular">Más populares</option>
                                <option value="trending">En tendencia</option>
                            </select>
                            
                            <button class="play-button" onclick="loadGlobalGoreVideos()" style="flex: 1; margin: 0;">
                                🔄 CARGAR
                            </button>
                        </div>
                        
                        <div style="display: flex; gap: 10px;">
                            <button class="download-btn" onclick="preloadCache()" style="flex: 1; margin: 0; font-size: 0.9em;">
                                ⚡ PRE-CARGAR TODOS
                            </button>
                            <button class="access-btn" onclick="clearCache()" style="flex: 1; margin: 0; font-size: 0.9em; background: rgba(255,0,85,0.2); border-color: var(--neon-red);">
                                🗑️ LIMPIAR CACHÉ
                            </button>
                        </div>
                    </div>
                    
                    <!-- Galería de videos globales -->
                    <div id="globalGoreGallery">
                        <div style="text-align: center; padding: 60px 20px; color: var(--blood-red);">
                            <div style="font-size: 3em; margin-bottom: 20px;">🌐</div>
                            <div style="font-size: 1.2em;">Selecciona un sitio para ver contenido</div>
                        </div>
                    </div>
                    
                    <!-- Paginación -->
                    <div id="globalPaginationControls" style="display: flex; gap: 10px; margin-top: 20px;"></div>
                </div>
            `;
        }

        let currentGlobalPage = 1;
        const globalItemsPerPage = 20;

        async function loadGlobalGoreVideos(page = 1) {
            const site = document.getElementById('globalGoreSite').value;
            const filter = document.getElementById('globalGoreFilter').value;
            const gallery = document.getElementById('globalGoreGallery');
            
            if (!site) {
                return;
            }
            
            gallery.innerHTML = `
                <div style="text-align: center; padding: 40px;">
                    <div class="loading-spinner"></div>
                    <div class="loading-text" style="color: var(--blood-red);">
                        🔄 Cargando videos de ${site}...<br>
                        <small>Primera carga puede tardar 10-20 segundos</small><br>
                        <small style="color: var(--neon-yellow);">Siguientes cargas serán instantáneas (caché 5 min)</small>
                    </div>
                </div>
            `;
            
            playBeep(1200, 100);
            
            const startTime = Date.now();
            
            try {
                const response = await fetch(`/global-gore/get-videos?site=${site}&filter=${filter}&page=${page}&limit=${globalItemsPerPage}`);
                const data = await response.json();
                
                const loadTime = ((Date.now() - startTime) / 1000).toFixed(1);
                
                if (!data.success) {
                    throw new Error(data.error || 'Error al cargar videos');
                }
                
                if (!data.videos || data.videos.length === 0) {
                    gallery.innerHTML = `
                        <div style="text-align: center; padding: 40px; color: var(--blood-red);">
                            ❌ No se encontraron videos<br>
                            <small>Intenta con otro sitio o filtro</small>
                        </div>
                    `;
                    return;
                }
                
                // Mostrar info de caché
                const cacheInfo = data.cached 
                    ? `<div style="background: rgba(57, 255, 20, 0.2); border: 1px solid var(--neon-green); padding: 10px; margin-bottom: 15px; text-align: center; color: var(--neon-green);">
                         ⚡ CACHÉ - Carga instantánea (${loadTime}s)
                       </div>`
                    : `<div style="background: rgba(255, 237, 0, 0.2); border: 1px solid var(--neon-yellow); padding: 10px; margin-bottom: 15px; text-align: center; color: var(--neon-yellow);">
                         🔄 NUEVO SCRAPING - Guardado en caché por 5 minutos (${loadTime}s)
                       </div>`;
                
                // Crear galería
                gallery.innerHTML = cacheInfo + `
                    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px;">
                        ${data.videos.map((video, index) => `
                            <div style="
                                border: 2px solid var(--blood-red);
                                padding: 15px;
                                background: rgba(139, 0, 0, 0.1);
                                cursor: pointer;
                                transition: all 0.3s;
                                position: relative;
                            " onmouseover="this.style.borderColor='var(--neon-red)'; this.style.background='rgba(255, 0, 85, 0.2)'"
                               onmouseout="this.style.borderColor='var(--blood-red)'; this.style.background='rgba(139, 0, 0, 0.1)'"
                               onclick="playGlobalGoreVideo('${encodeURIComponent(video.url)}', '${encodeURIComponent(video.title)}')">
                                
                                <!-- Indicador de streaming -->
                                <div style="
                                    position: absolute;
                                    top: 10px;
                                    right: 10px;
                                    background: var(--neon-red);
                                    color: #000;
                                    padding: 5px 10px;
                                    font-size: 0.7em;
                                    font-weight: bold;
                                    animation: statusBlink 1s infinite;
                                ">
                                    🔴 LIVE
                                </div>
                                
                                <!-- Thumbnail placeholder -->
                                <div style="
                                    width: 100%;
                                    height: 180px;
                                    background: linear-gradient(135deg, #1a0000 0%, #330000 100%);
                                    margin-bottom: 12px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    color: var(--blood-red);
                                    font-size: 3em;
                                    border: 1px solid var(--blood-red);
                                ">
                                    ${video.thumbnail ? `<img src="${video.thumbnail}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.style.display='none'">` : '▶'}
                                </div>
                                
                                <!-- Título del video -->
                                <div style="
                                    color: var(--neon-red); 
                                    font-weight: bold; 
                                    margin-bottom: 8px; 
                                    font-size: 0.95em; 
                                    word-break: break-word;
                                    line-height: 1.3;
                                    min-height: 40px;
                                ">
                                    ${video.title}
                                </div>
                                
                                <!-- Metadata -->
                                <div style="
                                    display: flex;
                                    justify-content: space-between;
                                    align-items: center;
                                    margin-top: 10px;
                                    padding-top: 10px;
                                    border-top: 1px solid rgba(139, 0, 0, 0.3);
                                ">
                                    <div style="color: var(--blood-red); font-size: 0.75em;">
                                        📅 ${video.date || 'Reciente'}
                                    </div>
                                    <div style="color: var(--neon-yellow); font-size: 0.75em;">
                                        👁️ ${video.views || '---'}
                                    </div>
                                </div>
                                
                                <!-- Sitio de origen -->
                                <div style="
                                    margin-top: 8px;
                                    color: var(--neon-blue);
                                    font-size: 0.7em;
                                    text-align: center;
                                    padding: 5px;
                                    background: rgba(0, 243, 255, 0.1);
                                    border-radius: 3px;
                                ">
                                    🌐 ${video.source || site.toUpperCase()}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
                
                // Controles de paginación
                const paginationControls = document.getElementById('globalPaginationControls');
                const totalPages = data.totalPages || 1;
                
                paginationControls.innerHTML = `
                    <button 
                        class="access-btn" 
                        onclick="loadGlobalGoreVideos(${page - 1})"
                        ${page <= 1 ? 'disabled' : ''}
                        style="flex: 1; ${page <= 1 ? 'opacity: 0.5; cursor: not-allowed;' : ''}"
                    >
                        ← ANTERIOR
                    </button>
                    
                    <div style="
                        flex: 1;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: var(--blood-red);
                        border: 2px solid var(--blood-red);
                        padding: 15px;
                        font-weight: bold;
                    ">
                        Página ${page} de ${totalPages}
                    </div>
                    
                    <button 
                        class="access-btn" 
                        onclick="loadGlobalGoreVideos(${page + 1})"
                        ${page >= totalPages ? 'disabled' : ''}
                        style="flex: 1; ${page >= totalPages ? 'opacity: 0.5; cursor: not-allowed;' : ''}"
                    >
                        SIGUIENTE →
                    </button>
                `;
                
                currentGlobalPage = page;
                playSuccessSound();
                
            } catch (error) {
                console.error('Error loading global gore videos:', error);
                playErrorSound();
                gallery.innerHTML = `
                    <div class="error-message">
                        ❌ Error al cargar videos: ${error.message}<br>
                        <small>Intenta con otro sitio</small>
                    </div>
                `;
            }
        }

        function playGlobalGoreVideo(encodedUrl, encodedTitle) {
            const url = decodeURIComponent(encodedUrl);
            const title = decodeURIComponent(encodedTitle);
            
            playSuccessSound();
            
            // Abrir en nueva ventana con reproductor especial
            window.open(`/global-gore/play?url=${encodedUrl}&title=${encodedTitle}`, '_blank');
        }

        async function preloadCache() {
            const statusDiv = document.getElementById('globalGoreGallery');
            const sites = ['kaotic', 'seegore'];
            
            statusDiv.innerHTML = `
                <div style="text-align: center; padding: 40px;">
                    <div class="loading-spinner"></div>
                    <div class="loading-text" style="color: var(--neon-yellow);">
                        ⚡ Pre-cargando caché de todos los sitios...<br>
                        <small>Esto tomará 20-40 segundos</small>
                    </div>
                    <div id="preloadProgress" style="margin-top: 20px; color: var(--neon-blue);"></div>
                </div>
            `;
            
            playBeep(1500, 100);
            
            let completed = 0;
            const progressDiv = document.getElementById('preloadProgress');
            
            for (const site of sites) {
                try {
                    progressDiv.innerHTML = `📥 Cargando ${site}... (${completed + 1}/${sites.length})`;
                    
                    await fetch(`/global-gore/get-videos?site=${site}&filter=recent&page=1&limit=20`);
                    
                    completed++;
                    progressDiv.innerHTML = `✅ ${site} completado (${completed}/${sites.length})`;
                    
                    playBeep(1000, 50);
                    await new Promise(resolve => setTimeout(resolve, 1000));
                    
                } catch (error) {
                    progressDiv.innerHTML += `<br>❌ Error en ${site}`;
                }
            }
            
            playSuccessSound();
            statusDiv.innerHTML = `
                <div style="text-align: center; padding: 60px; color: var(--neon-green);">
                    <div style="font-size: 4em; margin-bottom: 20px;">✅</div>
                    <div style="font-size: 1.5em; margin-bottom: 10px;">¡Caché Pre-cargado!</div>
                    <div style="font-size: 0.9em; color: var(--neon-blue);">
                        Ahora puedes cargar videos de forma instantánea<br>
                        Duración del caché: 5 minutos
                    </div>
                    <button class="play-button" onclick="document.getElementById('globalGoreSite').value='kaotic'; loadGlobalGoreVideos();" style="margin-top: 20px;">
                        Ver Videos de Kaotic
                    </button>
                </div>
            `;
        }

        async function clearCache() {
            playBeep(800, 100);
            
            try {
                await fetch('/global-gore/clear-cache', { method: 'POST' });
                
                playSuccessSound();
                document.getElementById('globalGoreGallery').innerHTML = `
                    <div style="text-align: center; padding: 60px; color: var(--neon-yellow);">
                        <div style="font-size: 4em; margin-bottom: 20px;">🗑️</div>
                        <div style="font-size: 1.3em;">Caché limpiado</div>
                        <div style="font-size: 0.9em; margin-top: 10px; color: var(--neon-blue);">
                            La próxima carga será desde cero
                        </div>
                    </div>
                `;
            } catch (error) {
                playErrorSound();
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // PANEL DE LIVE GORE
        // ═══════════════════════════════════════════════════════════════
        
        async function showLiveGorePanel() {
            const content = document.getElementById('content');
            const t = translations[currentLang];
            
            content.innerHTML = `
                <div class="video-info">
                    <div class="video-header">
                        <div class="video-title" style="color: var(--neon-red);">
                            🔴 LIVE GORE CONTENT
                        </div>
                    </div>
                    
                    <div class="warning-box" style="margin-bottom: 25px;">
                        <div class="warning-text">
                            ⚠️ CONTENIDO EXTREMO EN TIEMPO REAL<br>
                            Este contenido puede ser perturbador. Solo para mayores de edad.
                        </div>
                    </div>
                    
                    <!-- Galería de contenido -->
                    <div id="liveGoreGallery">
                        <div class="loading-text">Cargando contenido...</div>
                    </div>
                    
                    <!-- Paginación -->
                    <div style="display: flex; gap: 10px; margin-top: 20px;" id="paginationControls"></div>
                </div>
            `;
            
            loadLiveGoreContent(1);
        }

        let currentPage = 1;
        const itemsPerPage = 12;

        async function loadLiveGoreContent(page = 1) {
            try {
                const response = await fetch(`/livegore/get-content?page=${page}&limit=${itemsPerPage}`);
                const data = await response.json();
                
                const gallery = document.getElementById('liveGoreGallery');
                
                if (!data.items || data.items.length === 0) {
                    gallery.innerHTML = `
                        <div style="text-align: center; padding: 40px; color: var(--neon-red);">
                            No hay contenido disponible
                        </div>
                    `;
                    return;
                }
                
                // Crear galería en grid
                gallery.innerHTML = `
                    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px;">
                        ${data.items.map((item, index) => `
                            <div style="
                                border: 2px solid var(--neon-blue);
                                padding: 15px;
                                background: rgba(0, 243, 255, 0.05);
                                cursor: pointer;
                                transition: all 0.3s;
                            " onmouseover="this.style.borderColor='var(--neon-red)'; this.style.background='rgba(255, 0, 85, 0.1)'"
                               onmouseout="this.style.borderColor='var(--neon-blue)'; this.style.background='rgba(0, 243, 255, 0.05)'"
                               onclick="playLiveGoreItem('${item.filename}')">
                                
                                <div style="
                                    width: 100%;
                                    height: 160px;
                                    background: #000;
                                    margin-bottom: 10px;
                                    display: flex;
                                    align-items: center;
                                    justify-content: center;
                                    color: var(--neon-green);
                                    font-size: 3em;
                                ">
                                    ${item.type === 'video' ? '▶' : item.type === 'audio' ? '🎵' : '🖼️'}
                                </div>
                                
                                <div style="color: var(--neon-yellow); font-weight: bold; margin-bottom: 5px; font-size: 0.9em; word-break: break-word;">
                                    ${item.title || item.filename}
                                </div>
                                
                                <div style="color: var(--neon-blue); font-size: 0.8em;">
                                    ${item.size} | ${item.date}
                                </div>
                                
                                <div style="color: var(--neon-green); font-size: 0.75em; margin-top: 5px;">
                                    ${item.type.toUpperCase()}
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `;
                
                // Controles de paginación
                const paginationControls = document.getElementById('paginationControls');
                const totalPages = data.totalPages || 1;
                
                paginationControls.innerHTML = `
                    <button 
                        class="access-btn" 
                        onclick="loadLiveGoreContent(${page - 1})"
                        ${page <= 1 ? 'disabled' : ''}
                        style="flex: 1; ${page <= 1 ? 'opacity: 0.5; cursor: not-allowed;' : ''}"
                    >
                        ← ANTERIOR
                    </button>
                    
                    <div style="
                        flex: 1;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: var(--neon-blue);
                        border: 2px solid var(--neon-blue);
                        padding: 15px;
                    ">
                        Página ${page} de ${totalPages}
                    </div>
                    
                    <button 
                        class="access-btn" 
                        onclick="loadLiveGoreContent(${page + 1})"
                        ${page >= totalPages ? 'disabled' : ''}
                        style="flex: 1; ${page >= totalPages ? 'opacity: 0.5; cursor: not-allowed;' : ''}"
                    >
                        SIGUIENTE →
                    </button>
                `;
                
                currentPage = page;
                
            } catch (error) {
                console.error('Error loading live gore content:', error);
                document.getElementById('liveGoreGallery').innerHTML = `
                    <div class="error-message">Error cargando contenido</div>
                `;
            }
        }

        function playLiveGoreItem(filename) {
            playSuccessSound();
            window.open(`/livegore/play?file=${encodeURIComponent(filename)}`, '_blank');
        }

        // ═══════════════════════════════════════════════════════════════
        // PANEL DE ADMINISTRACIÓN
        // ═══════════════════════════════════════════════════════════════
        
        async function showAdminPanel() {
            const content = document.getElementById('content');
            const t = translations[currentLang];
            
            content.innerHTML = `
                <div class="video-info">
                    <div class="video-header">
                        <div class="video-title">${t.adminPanel}</div>
                    </div>
                    
                    <div class="admin-section">
                        <h3>${t.selectFile}</h3>
                        
                        <!-- Subir nuevo archivo -->
                        <div style="margin-bottom: 20px;">
                            <input 
                                type="file" 
                                id="fileUpload" 
                                accept="video/*,audio/*,image/*"
                                style="display: none;"
                                onchange="uploadFile()"
                            >
                            <button 
                                class="play-button" 
                                onclick="document.getElementById('fileUpload').click()"
                                style="margin-bottom: 10px;"
                            >
                                📤 SUBIR ARCHIVO DESDE MI DISPOSITIVO
                            </button>
                            <div id="uploadStatus"></div>
                        </div>
                        
                        <!-- Cargar desde URL/API -->
                        <div style="margin-bottom: 20px; border: 2px solid var(--neon-yellow); padding: 15px; background: rgba(255, 237, 0, 0.05);">
                            <h4 style="color: var(--neon-yellow); margin-bottom: 10px;">🌐 DESCARGAR CONTENIDO</h4>
                            
                            <input 
                                type="text" 
                                class="admin-input" 
                                id="videoUrl" 
                                placeholder="URL (YouTube, TikTok, sitios gore, etc.)"
                                style="margin-bottom: 10px;"
                            >
                            
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
                                <button 
                                    class="play-button" 
                                    onclick="downloadWithYtDlp()"
                                    style="margin: 0;"
                                >
                                    📹 YT-DLP
                                </button>
                                
                                <button 
                                    class="download-btn" 
                                    onclick="downloadWithTikWM()"
                                    style="margin: 0;"
                                >
                                    📱 TikWM
                                </button>
                            </div>
                            
                            <button 
                                class="access-btn" 
                                onclick="downloadFromUrl()"
                                style="margin-bottom: 10px;"
                            >
                                ⬇️ DESCARGA DIRECTA
                            </button>
                            
                            <div id="urlStatus" style="margin-top: 10px;"></div>
                        </div>
                        
                        <!-- Scraper de sitios GORE -->
                        <div style="margin-bottom: 20px; border: 2px solid var(--neon-red); padding: 15px; background: rgba(255, 0, 85, 0.05);">
                            <h4 style="color: var(--neon-red); margin-bottom: 10px;">🔴 SCRAPER DE SITIOS GORE</h4>
                            
                            <select class="admin-input" id="goreSite" style="margin-bottom: 10px;">
                                <option value="">Selecciona un sitio</option>
                                <option value="kaotic">Kaotic</option>
                                <option value="seegore">SeeGore</option>
                                <option value="theync">TheYNC</option>
                                <option value="hoodsite">HoodSite</option>
                                <option value="custom">URL Personalizada</option>
                            </select>
                            
                            <input 
                                type="number" 
                                class="admin-input" 
                                id="goreLimit" 
                                placeholder="Cantidad de videos (1-50)"
                                min="1"
                                max="50"
                                value="10"
                                style="margin-bottom: 10px;"
                            >
                            
                            <div style="display: flex; gap: 10px;">
                                <label style="flex: 1; color: var(--neon-blue); display: flex; align-items: center; gap: 8px; cursor: pointer;">
                                    <input type="checkbox" id="includeUncensored" checked>
                                    Sin censura
                                </label>
                                <label style="flex: 1; color: var(--neon-yellow); display: flex; align-items: center; gap: 8px; cursor: pointer;">
                                    <input type="checkbox" id="includeCensored">
                                    Censurados
                                </label>
                            </div>
                            
                            <button 
                                class="access-btn" 
                                onclick="scrapGoreSite()"
                                style="margin-top: 10px; background: var(--neon-red); border-color: var(--neon-red);"
                            >
                                🔴 INICIAR SCRAPING
                            </button>
                            
                            <div id="scrapeStatus" style="margin-top: 10px;"></div>
                            <div id="scrapeProgress" style="margin-top: 10px;"></div>
                        </div>
                        
                        <div class="file-list" id="fileList">
                            <div class="loading-text">Cargando archivos...</div>
                        </div>
                        <div style="margin-top: 10px; color: var(--neon-blue); font-size: 0.9em;">
                            Archivo actual: <span id="currentFileName">Ninguno</span>
                        </div>
                    </div>
                    
                    <div class="admin-section">
                        <h3>Información (Español)</h3>
                        <input type="text" class="admin-input" id="title-es" placeholder="Título">
                        <textarea class="admin-textarea" id="context-es" placeholder="Contexto"></textarea>
                        <textarea class="admin-textarea" id="warning-es" placeholder="Advertencia"></textarea>
                        <input type="text" class="admin-input" id="duration" placeholder="Duración (ej: 15:47)">
                        <input type="text" class="admin-input" id="classification-es" placeholder="Clasificación">
                    </div>
                    
                    <div class="admin-section">
                        <h3>Información (Inglés)</h3>
                        <input type="text" class="admin-input" id="title-en" placeholder="Title">
                        <textarea class="admin-textarea" id="context-en" placeholder="Context"></textarea>
                        <textarea class="admin-textarea" id="warning-en" placeholder="Warning"></textarea>
                        <input type="text" class="admin-input" id="classification-en" placeholder="Classification">
                    </div>
                    
                    <button class="access-btn" onclick="saveAdminChanges()">
                        💾 GUARDAR CAMBIOS
                    </button>
                    
                    <button class="play-button" onclick="loadVideoInfo(); isAdmin = false;">
                        👁️ VER COMO USUARIO
                    </button>
                    
                    <div id="admin-status"></div>
                </div>
            `;
            
            loadAdminData();
            loadFileList();
        }

        async function loadFileList() {
            try {
                const response = await fetch('/admin/get-files');
                const data = await response.json();
                const fileList = document.getElementById('fileList');
                const t = translations[currentLang];
                
                if (data.files.length === 0) {
                    fileList.innerHTML = `<div style="color: var(--neon-red); text-align: center; padding: 20px;">${t.noFiles}<br><br>Usa el botón "SUBIR ARCHIVO" para agregar contenido</div>`;
                    return;
                }
                
                fileList.innerHTML = data.files.map(file => `
                    <div class="file-item ${file.name === data.current ? 'selected' : ''}" 
                         onclick="selectFile('${file.name}')">
                        <div style="color: var(--neon-blue); font-weight: bold;">${file.name}</div>
                        <div style="color: var(--neon-green); font-size: 0.9em;">${file.size}</div>
                    </div>
                `).join('');
                
                if (data.current) {
                    document.getElementById('currentFileName').textContent = data.current;
                    document.getElementById('currentFileName').style.color = 'var(--neon-green)';
                    currentFile = data.current;
                } else {
                    document.getElementById('currentFileName').textContent = 'Ninguno seleccionado';
                    document.getElementById('currentFileName').style.color = 'var(--neon-red)';
                }
            } catch (error) {
                console.error('Error loading files:', error);
            }
        }

        function selectFile(filename) {
            currentFile = filename;
            document.querySelectorAll('.file-item').forEach(item => {
                item.classList.remove('selected');
            });
            event.target.closest('.file-item').classList.add('selected');
            document.getElementById('currentFileName').textContent = filename;
            playBeep(1000, 50);
        }

        async function uploadFile() {
            const fileInput = document.getElementById('fileUpload');
            const file = fileInput.files[0];
            const statusDiv = document.getElementById('uploadStatus');
            
            if (!file) return;
            
            // Mostrar progreso
            statusDiv.innerHTML = `<div style="color: var(--neon-yellow); margin: 10px 0;">
                📤 Subiendo: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)...
            </div>`;
            
            playBeep(1200, 100);
            
            // Crear FormData
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch('/admin/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    playSuccessSound();
                    statusDiv.innerHTML = `<div style="color: var(--neon-green); margin: 10px 0;">
                        ✅ Archivo subido: ${result.filename}
                    </div>`;
                    
                    // Recargar lista de archivos
                    setTimeout(() => {
                        loadFileList();
                        statusDiv.innerHTML = '';
                    }, 2000);
                } else {
                    playErrorSound();
                    statusDiv.innerHTML = `<div class="error-message">
                        ❌ Error: ${result.error || 'Error desconocido'}
                    </div>`;
                }
            } catch (error) {
                playErrorSound();
                statusDiv.innerHTML = `<div class="error-message">
                    ❌ Error de conexión: ${error.message}
                </div>`;
            }
            
            // Limpiar input
            fileInput.value = '';
        }

        async function downloadFromUrl() {
            const urlInput = document.getElementById('videoUrl');
            const url = urlInput.value.trim();
            const statusDiv = document.getElementById('urlStatus');
            
            if (!url) {
                playBeep(300, 200);
                return;
            }
            
            // Validar URL
            try {
                new URL(url);
            } catch (e) {
                playErrorSound();
                statusDiv.innerHTML = `<div class="error-message">❌ URL inválida</div>`;
                return;
            }
            
            statusDiv.innerHTML = `<div style="color: var(--neon-yellow);">
                ⬇️ Descargando desde URL...
            </div>`;
            
            playBeep(1200, 100);
            
            try {
                const response = await fetch('/admin/download-url', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    playSuccessSound();
                    statusDiv.innerHTML = `<div style="color: var(--neon-green);">
                        ✅ Descargado: ${result.filename}
                    </div>`;
                    
                    setTimeout(() => {
                        loadFileList();
                        urlInput.value = '';
                        statusDiv.innerHTML = '';
                    }, 2000);
                } else {
                    playErrorSound();
                    statusDiv.innerHTML = `<div class="error-message">
                        ❌ Error: ${result.error || 'No se pudo descargar'}
                    </div>`;
                }
            } catch (error) {
                playErrorSound();
                statusDiv.innerHTML = `<div class="error-message">
                    ❌ Error de conexión
                </div>`;
            }
        }

        async function downloadWithYtDlp() {
            const urlInput = document.getElementById('videoUrl');
            const url = urlInput.value.trim();
            const statusDiv = document.getElementById('urlStatus');
            
            if (!url) {
                playBeep(300, 200);
                statusDiv.innerHTML = `<div class="error-message">❌ Ingresa una URL</div>`;
                return;
            }
            
            statusDiv.innerHTML = `<div style="color: var(--neon-yellow);">
                📹 Descargando con YT-DLP...<br>
                <small>Esto puede tardar varios minutos dependiendo del tamaño</small>
            </div>`;
            
            playBeep(1200, 100);
            
            try {
                const response = await fetch('/admin/download-ytdlp', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    playSuccessSound();
                    statusDiv.innerHTML = `<div style="color: var(--neon-green);">
                        ✅ Descargado: ${result.filename}<br>
                        <small>${result.size || ''}</small>
                    </div>`;
                    
                    setTimeout(() => {
                        loadFileList();
                        urlInput.value = '';
                        statusDiv.innerHTML = '';
                    }, 3000);
                } else {
                    playErrorSound();
                    statusDiv.innerHTML = `<div class="error-message">
                        ❌ Error: ${result.error || 'No se pudo descargar'}<br>
                        <small>Asegúrate de tener yt-dlp instalado</small>
                    </div>`;
                }
            } catch (error) {
                playErrorSound();
                statusDiv.innerHTML = `<div class="error-message">
                    ❌ Error de conexión
                </div>`;
            }
        }

        async function downloadWithTikWM() {
            const urlInput = document.getElementById('videoUrl');
            const url = urlInput.value.trim();
            const statusDiv = document.getElementById('urlStatus');
            
            if (!url) {
                playBeep(300, 200);
                statusDiv.innerHTML = `<div class="error-message">❌ Ingresa una URL de TikTok</div>`;
                return;
            }
            
            if (!url.includes('tiktok.com')) {
                playErrorSound();
                statusDiv.innerHTML = `<div class="error-message">❌ Solo URLs de TikTok</div>`;
                return;
            }
            
            statusDiv.innerHTML = `<div style="color: var(--neon-yellow);">
                📱 Descargando con TikWM API...
            </div>`;
            
            playBeep(1200, 100);
            
            try {
                const response = await fetch('/admin/download-tikwm', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    playSuccessSound();
                    statusDiv.innerHTML = `<div style="color: var(--neon-green);">
                        ✅ Descargado: ${result.filename}<br>
                        <small>Tipo: ${result.type || 'video'}</small>
                    </div>`;
                    
                    setTimeout(() => {
                        loadFileList();
                        urlInput.value = '';
                        statusDiv.innerHTML = '';
                    }, 3000);
                } else {
                    playErrorSound();
                    statusDiv.innerHTML = `<div class="error-message">
                        ❌ Error: ${result.error || 'No se pudo descargar'}
                    </div>`;
                }
            } catch (error) {
                playErrorSound();
                statusDiv.innerHTML = `<div class="error-message">
                    ❌ Error de conexión
                </div>`;
            }
        }

        async function scrapGoreSite() {
            const site = document.getElementById('goreSite').value;
            const limit = parseInt(document.getElementById('goreLimit').value) || 10;
            const includeUncensored = document.getElementById('includeUncensored').checked;
            const includeCensored = document.getElementById('includeCensored').checked;
            const statusDiv = document.getElementById('scrapeStatus');
            const progressDiv = document.getElementById('scrapeProgress');
            
            if (!site) {
                playBeep(300, 200);
                statusDiv.innerHTML = `<div class="error-message">❌ Selecciona un sitio</div>`;
                return;
            }
            
            if (!includeUncensored && !includeCensored) {
                playErrorSound();
                statusDiv.innerHTML = `<div class="error-message">❌ Selecciona al menos un tipo de contenido</div>`;
                return;
            }
            
            statusDiv.innerHTML = `<div style="color: var(--neon-red);">
                🔴 Iniciando scraping de ${site}...<br>
                <small>Esto puede tardar varios minutos</small>
            </div>`;
            progressDiv.innerHTML = `<div style="color: var(--neon-yellow);">
                📊 Procesando: 0/${limit} videos
            </div>`;
            
            playBeep(1200, 100);
            
            try {
                const response = await fetch('/admin/scrape-gore', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        site: site,
                        limit: limit,
                        uncensored: includeUncensored,
                        censored: includeCensored
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    playSuccessSound();
                    statusDiv.innerHTML = `<div style="color: var(--neon-green);">
                        ✅ Scraping completado<br>
                        <small>Descargados: ${result.downloaded} / ${result.total} videos</small>
                    </div>`;
                    progressDiv.innerHTML = `<div style="color: var(--neon-green);">
                        ${result.files.map(f => `📹 ${f}`).join('<br>')}
                    </div>`;
                    
                    setTimeout(() => {
                        loadFileList();
                        statusDiv.innerHTML = '';
                        progressDiv.innerHTML = '';
                    }, 5000);
                } else {
                    playErrorSound();
                    statusDiv.innerHTML = `<div class="error-message">
                        ❌ Error: ${result.error || 'No se pudo hacer scraping'}
                    </div>`;
                    progressDiv.innerHTML = '';
                }
            } catch (error) {
                playErrorSound();
                statusDiv.innerHTML = `<div class="error-message">
                    ❌ Error de conexión
                </div>`;
                progressDiv.innerHTML = '';
            }
        }

        async function loadAdminData() {
            try {
                const response = await fetch('/admin/get-config');
                const config = await response.json();
                
                document.getElementById('title-es').value = config.video_data.es.title;
                document.getElementById('context-es').value = config.video_data.es.context;
                document.getElementById('warning-es').value = config.video_data.es.warning;
                document.getElementById('duration').value = config.video_data.es.duration;
                document.getElementById('classification-es').value = config.video_data.es.classification;
                
                document.getElementById('title-en').value = config.video_data.en.title;
                document.getElementById('context-en').value = config.video_data.en.context;
                document.getElementById('warning-en').value = config.video_data.en.warning;
                document.getElementById('classification-en').value = config.video_data.en.classification;
            } catch (error) {
                console.error('Error loading admin data:', error);
            }
        }

        async function saveAdminChanges() {
            const statusDiv = document.getElementById('admin-status');
            
            // Verificar que hay un archivo seleccionado
            if (!currentFile) {
                playErrorSound();
                statusDiv.innerHTML = `<div class="error-message">❌ Debes seleccionar un archivo primero</div>`;
                return;
            }
            
            const newConfig = {
                video_data: {
                    es: {
                        title: document.getElementById('title-es').value,
                        context: document.getElementById('context-es').value,
                        warning: document.getElementById('warning-es').value,
                        duration: document.getElementById('duration').value,
                        date: new Date().toLocaleDateString('es-ES'),
                        classification: document.getElementById('classification-es').value
                    },
                    en: {
                        title: document.getElementById('title-en').value,
                        context: document.getElementById('context-en').value,
                        warning: document.getElementById('warning-en').value,
                        duration: document.getElementById('duration').value,
                        date: new Date().toLocaleDateString('en-US'),
                        classification: document.getElementById('classification-en').value
                    }
                },
                current_file: currentFile
            };
            
            try {
                playBeep(1500, 100);
                const response = await fetch('/admin/update-config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(newConfig)
                });
                
                const result = await response.json();
                
                if (result.success) {
                    playSuccessSound();
                    statusDiv.innerHTML = `<div class="status-bar">✅ Cambios guardados exitosamente. Archivo: ${currentFile}</div>`;
                } else {
                    playErrorSound();
                    statusDiv.innerHTML = `<div class="error-message">❌ Error al guardar</div>`;
                }
            } catch (error) {
                playErrorSound();
                statusDiv.innerHTML = `<div class="error-message">❌ Error de conexión</div>`;
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // CARGAR INFORMACIÓN DEL VIDEO
        // ═══════════════════════════════════════════════════════════════
        
        async function loadVideoInfo() {
            const content = document.getElementById('content');
            const t = translations[currentLang];
            
            try {
                const response = await fetch(`/data?lang=${currentLang}`);
                const data = await response.json();
                
                // Verificar si hay archivo seleccionado
                const fileCheck = await fetch('/admin/get-files');
                const fileData = await fileCheck.json();
                
                if (!fileData.current) {
                    content.innerHTML = `
                        <div class="video-info">
                            <div class="error-message" style="margin: 40px 0; padding: 30px;">
                                ❌ NO HAY CONTENIDO DISPONIBLE
                                <br><br>
                                El administrador debe seleccionar un archivo primero.
                            </div>
                        </div>
                    `;
                    return;
                }
                
                content.innerHTML = `
                    <div class="video-info">
                        <div class="video-header">
                            <div class="video-title">${data.title}</div>
                            <div class="video-meta">
                                <div class="classification">${data.classification}</div>
                                <div>${data.date} | ${data.duration}</div>
                            </div>
                        </div>
                        
                        <div class="video-context">${data.context}</div>
                        
                        <div class="warning-box">
                            <div class="warning-text">${data.warning}</div>
                        </div>
                        
                        <button class="play-button" onclick="playVideo()">
                            ${t.playButton}
                        </button>
                        
                        <button class="download-btn" onclick="openDownloadModal()">
                            ${t.downloadButton}
                        </button>
                        
                        <div class="status-bar">
                            ${currentLang === 'es' ? 'LISTO PARA REPRODUCIR' : 'READY TO PLAY'}
                        </div>
                    </div>
                `;
            } catch (error) {
                console.error('Error loading video info:', error);
                content.innerHTML = `
                    <div class="error-message" style="margin: 40px 0;">
                        ❌ Error al cargar información
                    </div>
                `;
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // REPRODUCIR VIDEO
        // ═══════════════════════════════════════════════════════════════
        
        function playVideo() {
            playSuccessSound();
            window.open('/play', '_blank');
        }

        // ═══════════════════════════════════════════════════════════════
        // SISTEMA DE DESCARGA CON PROTECCIÓN
        // ═══════════════════════════════════════════════════════════════
        
        function openDownloadModal() {
            playBeep(1200, 100);
            document.getElementById('downloadModal').classList.add('active');
            document.getElementById('download-key').value = '';
            document.getElementById('download-error').innerHTML = '';
        }

        function closeDownloadModal() {
            playBeep(800, 100);
            document.getElementById('downloadModal').classList.remove('active');
        }

        async function verifyDownload() {
            const keyInput = document.getElementById('download-key');
            const key = keyInput.value.trim().toUpperCase();
            const errorDiv = document.getElementById('download-error');
            
            if (!key) {
                playBeep(300, 200);
                return;
            }

            try {
                const response = await fetch('/verify-download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key: key })
                });

                const result = await response.json();

                if (result.valid) {
                    playSuccessSound();
                    closeDownloadModal();
                    window.location.href = '/download';
                } else {
                    playErrorSound();
                    errorDiv.innerHTML = `<div class="error-message">${currentLang === 'es' ? '❌ Código incorrecto' : '❌ Invalid code'}</div>`;
                    keyInput.value = '';
                }
            } catch (error) {
                playErrorSound();
                errorDiv.innerHTML = `<div class="error-message">${currentLang === 'es' ? '❌ Error de servidor' : '❌ Server error'}</div>`;
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // INICIALIZACIÓN
        // ═══════════════════════════════════════════════════════════════
        
        window.addEventListener('DOMContentLoaded', () => {
            setTimeout(() => {
                showAccessForm();
            }, 1500);
        });
    </script>
</body>
</html>
"""

# ═══════════════════════════════════════════════════════════════
# FUNCIONES DE SCRAPING DE SITIOS GORE
# ═══════════════════════════════════════════════════════════════

def scrape_generic_gore_site(base_url, limit, include_uncensored, include_censored):
    """
    Scraper genérico para sitios gore
    NOTA: Este es un scraper básico que usa yt-dlp para descargar videos
    """
    downloaded_files = []
    
    try:
        # Usar yt-dlp para extraer videos del sitio
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for i in range(limit):
            try:
                # Intentar descargar usando yt-dlp del sitio
                output_template = os.path.join(MEDIA_DIR, f'gore_{timestamp}_{i}_%(title)s.%(ext)s')
                
                result = subprocess.run([
                    'yt-dlp',
                    '--no-playlist',
                    '--max-downloads', '1',
                    '--skip-download',  # Solo obtener info
                    '--get-url',
                    '--get-title',
                    base_url
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    # Descargar el video encontrado
                    subprocess.run([
                        'yt-dlp',
                        '-f', 'best',
                        '--no-playlist',
                        '-o', output_template,
                        base_url
                    ], timeout=120)
                    
                    # Buscar archivo descargado
                    new_files = [f for f in os.listdir(MEDIA_DIR) if f.startswith(f'gore_{timestamp}_{i}_')]
                    if new_files:
                        downloaded_files.extend(new_files)
                        print(f"  ✅ Descargado: {new_files[0]}")
                    
                time.sleep(2)  # Delay entre descargas
                
            except Exception as e:
                print(f"  ⚠️ Error en video {i+1}: {str(e)}")
                continue
        
    except Exception as e:
        print(f"❌ Error general en scraping: {str(e)}")
    
    return downloaded_files

def scrape_kaotic(limit, include_uncensored, include_censored):
    """Scraper para Kaotic.com"""
    print("📥 Scraping Kaotic.com...")
    
    try:
        # URL de videos recientes de Kaotic
        base_url = "https://www.kaotic.com/videos"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(base_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar enlaces de videos
        video_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/video/' in href:
                full_url = 'https://www.kaotic.com' + href if href.startswith('/') else href
                video_links.append(full_url)
        
        video_links = list(set(video_links))[:limit]  # Eliminar duplicados
        
        downloaded_files = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for idx, url in enumerate(video_links):
            try:
                print(f"  📹 Descargando {idx+1}/{len(video_links)}: {url}")
                
                output_template = os.path.join(MEDIA_DIR, f'kaotic_{timestamp}_{idx}_%(title)s.%(ext)s')
                
                result = subprocess.run([
                    'yt-dlp',
                    '-f', 'best',
                    '--no-playlist',
                    '-o', output_template,
                    url
                ], capture_output=True, text=True, timeout=120)
                
                if result.returncode == 0:
                    new_files = [f for f in os.listdir(MEDIA_DIR) if f.startswith(f'kaotic_{timestamp}_{idx}_')]
                    if new_files:
                        downloaded_files.extend(new_files)
                        print(f"    ✅ Éxito: {new_files[0]}")
                
                time.sleep(3)  # Delay entre descargas
                
            except Exception as e:
                print(f"    ⚠️ Error: {str(e)}")
                continue
        
        return downloaded_files
        
    except Exception as e:
        print(f"❌ Error en Kaotic: {str(e)}")
        return []

def scrape_seegore(limit, include_uncensored, include_censored):
    """Scraper para SeeGore.com"""
    print("📥 Scraping SeeGore...")
    return scrape_generic_gore_site("https://seegore.com", limit, include_uncensored, include_censored)

def scrape_theync(limit, include_uncensored, include_censored):
    """Scraper para TheYNC.com"""
    print("📥 Scraping TheYNC...")
    return scrape_generic_gore_site("https://www.theync.com", limit, include_uncensored, include_censored)

def scrape_hoodsite(limit, include_uncensored, include_censored):
    """Scraper para HoodSite.com"""
    print("📥 Scraping HoodSite...")
    return scrape_generic_gore_site("https://hoodsite.com", limit, include_uncensored, include_censored)

# ═══════════════════════════════════════════════════════════════
# FUNCIONES PARA GLOBAL GORE (NOA666)
# ═══════════════════════════════════════════════════════════════

def get_global_gore_videos(site, filter_type, page, limit):
    """
    Obtener videos de sitios gore sin descargarlos
    Usa CACHE para evitar scraping repetido
    """
    cache_key = f"{site}_{filter_type}"
    current_time = time.time()
    
    # Verificar si hay cache válido
    if cache_key in GLOBAL_GORE_CACHE:
        cache_data = GLOBAL_GORE_CACHE[cache_key]
        if current_time - cache_data['timestamp'] < CACHE_DURATION:
            print(f"  ✅ Usando cache para {site} (edad: {int(current_time - cache_data['timestamp'])}s)")
            videos = cache_data['videos']
            
            # Paginación desde cache
            start = (page - 1) * limit
            end = start + limit
            total_pages = (len(videos) + limit - 1) // limit
            
            return {
                'success': True,
                'videos': videos[start:end],
                'page': page,
                'totalPages': total_pages,
                'total': len(videos),
                'cached': True
            }
    
    # Si no hay cache, hacer scraping
    print(f"🔄 Scraping {site} (sin cache)...")
    videos = []
    
    try:
        # URLs de los sitios según filtro
        site_urls = {
            'kaotic': 'https://www.kaotic.com/videos',
            'seegore': 'https://seegore.com',
            'theync': 'https://www.theync.com/gore',
            'hoodsite': 'https://hoodsite.com'
        }
        
        if site == 'all':
            # Para "todos", usar solo cache si existe
            all_videos = []
            for site_name in ['kaotic', 'seegore']:  # Reducir a 2 sitios para velocidad
                cache_key_temp = f"{site_name}_{filter_type}"
                if cache_key_temp in GLOBAL_GORE_CACHE:
                    cache_data = GLOBAL_GORE_CACHE[cache_key_temp]
                    if current_time - cache_data['timestamp'] < CACHE_DURATION:
                        all_videos.extend(cache_data['videos'][:10])  # Solo 10 de cada uno
            
            if all_videos:
                videos = all_videos
            else:
                # Si no hay cache, hacer scraping rápido solo de Kaotic
                videos = get_videos_from_site_fast(site_urls['kaotic'], 'kaotic', limit)
        else:
            base_url = site_urls.get(site)
            if base_url:
                videos = get_videos_from_site_fast(base_url, site, limit)
        
        # Guardar en cache
        GLOBAL_GORE_CACHE[cache_key] = {
            'videos': videos,
            'timestamp': current_time
        }
        print(f"  ✅ Cache actualizado para {site}")
        
        # Paginación
        start = (page - 1) * limit
        end = start + limit
        total_pages = (len(videos) + limit - 1) // limit
        
        return {
            'success': True,
            'videos': videos[start:end],
            'page': page,
            'totalPages': total_pages,
            'total': len(videos),
            'cached': False
        }
        
    except Exception as e:
        print(f"❌ Error obteniendo videos globales: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def get_videos_from_site_fast(base_url, site_name, limit):
    """
    Versión RÁPIDA del scraper
    Solo obtiene títulos y URLs, sin thumbnails ni metadata extra
    """
    videos = []
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"  📥 Scraping rápido de {site_name}...")
        
        # Timeout más corto
        response = requests.get(base_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar enlaces de videos
        video_links = []
        
        if site_name == 'kaotic':
            # Kaotic tiene estructura específica
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/video/' in href and len(video_links) < limit * 2:
                    full_url = 'https://www.kaotic.com' + href if href.startswith('/') else href
                    if full_url not in video_links:
                        video_links.append(full_url)
                        
                        # Intentar obtener título del link
                        title_elem = link.find('h2') or link.find('h3') or link.find('span', class_='title')
                        if title_elem:
                            title = title_elem.get_text().strip()[:80]
                        else:
                            title = link.get_text().strip()[:80] or 'Video sin título'
                        
                        videos.append({
                            'title': title,
                            'url': full_url,
                            'thumbnail': '',  # Sin thumbnail para velocidad
                            'date': 'Reciente',
                            'views': '---',
                            'source': site_name.upper()
                        })
                        
                        if len(videos) >= limit:
                            break
        else:
            # Búsqueda genérica para otros sitios
            for link in soup.find_all('a', href=True):
                if len(videos) >= limit:
                    break
                    
                href = link['href']
                if any(x in href.lower() for x in ['video', 'watch', 'v/']):
                    if href.startswith('http'):
                        full_url = href
                    elif href.startswith('/'):
                        full_url = base_url.rstrip('/') + href
                    else:
                        continue
                    
                    if full_url not in [v['url'] for v in videos]:
                        title = link.get_text().strip()[:80] or 'Video sin título'
                        
                        videos.append({
                            'title': title,
                            'url': full_url,
                            'thumbnail': '',
                            'date': 'Reciente',
                            'views': '---',
                            'source': site_name.upper()
                        })
        
        print(f"  ✅ Obtenidos {len(videos)} videos de {site_name} (modo rápido)")
        
    except Exception as e:
        print(f"  ❌ Error en {site_name}: {str(e)}")
    
    return videos

# ═══════════════════════════════════════════════════════════════
# SERVIDOR HTTP
# ═══════════════════════════════════════════════════════════════

class DarkNeonHandler(BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        """Log personalizado"""
        print(f"[{self.log_date_time_string()}] {format % args}")
    
    def do_GET(self):
        """Maneja peticiones GET"""
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        # Página principal
        if path == '/' or path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode('utf-8'))
        
        # Datos del video
        elif path == '/data':
            query = urllib.parse.parse_qs(parsed.query)
            lang = query.get('lang', ['es'])[0]
            data = VIDEO_DATA.get(lang, VIDEO_DATA['es'])
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        
        # Admin: Obtener configuración
        elif path == '/admin/get-config':
            config = {
                'video_data': VIDEO_DATA,
                'current_file': CURRENT_FILE
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(config, ensure_ascii=False).encode('utf-8'))
        
        # Admin: Obtener lista de archivos
        elif path == '/admin/get-files':
            files = get_available_files()
            response = {
                'files': files,
                'current': CURRENT_FILE
            }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        
        # Reproducir video (nueva ventana con player)
        elif path == '/play':
            if not CURRENT_FILE:
                self.send_error(404, "No hay archivo seleccionado")
                return
            
            file_path = os.path.join(MEDIA_DIR, CURRENT_FILE)
            if not os.path.exists(file_path):
                self.send_error(404, "Archivo no encontrado")
                return
            
            # HTML del reproductor
            player_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>▶ REPRODUCCIÓN</title>
    <style>
        body {{
            margin: 0;
            background: #000;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        video {{
            max-width: 100%;
            max-height: 100vh;
        }}
    </style>
</head>
<body>
    <video controls autoplay>
        <source src="/stream" type="{mimetypes.guess_type(CURRENT_FILE)[0] or 'video/mp4'}">
        Tu navegador no soporta video HTML5.
    </video>
</body>
</html>"""
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(player_html.encode('utf-8'))
        
        # Stream del video
        elif path == '/stream':
            if not CURRENT_FILE:
                self.send_error(404, "No hay archivo seleccionado")
                return
            
            file_path = os.path.join(MEDIA_DIR, CURRENT_FILE)
            if not os.path.exists(file_path):
                self.send_error(404, "Archivo no encontrado")
                return
            
            self.send_response(200)
            content_type = mimetypes.guess_type(CURRENT_FILE)[0] or 'application/octet-stream'
            self.send_header('Content-type', content_type)
            self.end_headers()
            
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        
        # Descargar archivo
        elif path == '/download':
            if not CURRENT_FILE:
                self.send_error(404, "No hay archivo seleccionado")
                return
            
            file_path = os.path.join(MEDIA_DIR, CURRENT_FILE)
            if not os.path.exists(file_path):
                self.send_error(404, "Archivo no encontrado")
                return
            
            self.send_response(200)
            content_type = mimetypes.guess_type(CURRENT_FILE)[0] or 'application/octet-stream'
            self.send_header('Content-type', content_type)
            self.send_header('Content-Disposition', f'attachment; filename="{CURRENT_FILE}"')
            self.end_headers()
            
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        
        # Live Gore: Obtener contenido
        elif path.startswith('/livegore/get-content'):
            handle_livegore_content(self)
        
        # Live Gore: Reproducir
        elif path.startswith('/livegore/play'):
            handle_livegore_play(self)
        
        # Live Gore: Stream
        elif path.startswith('/livegore/stream'):
            handle_livegore_stream(self)
        
        # Global Gore: Obtener videos
        elif path.startswith('/global-gore/get-videos'):
            parsed = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed.query)
            
            site = query.get('site', [''])[0]
            filter_type = query.get('filter', ['recent'])[0]
            page = int(query.get('page', ['1'])[0])
            limit = int(query.get('limit', ['20'])[0])
            
            result = get_global_gore_videos(site, filter_type, page, limit)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode('utf-8'))
        
        # Global Gore: Reproducir video directo
        elif path.startswith('/global-gore/play'):
            parsed = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed.query)
            
            url = query.get('url', [''])[0]
            title = query.get('title', ['Video'])[0]
            
            if not url:
                self.send_error(404, "URL no especificada")
                return
            
            # Decodificar URL
            url = urllib.parse.unquote(url)
            title = urllib.parse.unquote(title)
            
            # HTML del reproductor con streaming directo
            player_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>🔴 {title}</title>
    <style>
        body {{
            margin: 0;
            background: #000;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: 'Courier New', monospace;
        }}
        .header {{
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(139, 0, 0, 0.9);
            padding: 15px;
            text-align: center;
            color: #ff0055;
            font-size: 1.2em;
            border-bottom: 2px solid #ff0055;
            z-index: 1000;
            box-shadow: 0 0 20px rgba(255, 0, 85, 0.5);
        }}
        .video-container {{
            margin-top: 80px;
            width: 90%;
            max-width: 1200px;
        }}
        video {{
            width: 100%;
            max-height: 80vh;
            background: #000;
        }}
        .loading {{
            text-align: center;
            color: #ff0055;
            padding: 40px;
            font-size: 1.5em;
        }}
        .error {{
            text-align: center;
            color: #ff0055;
            padding: 40px;
            background: rgba(139, 0, 0, 0.3);
            border: 2px solid #ff0055;
            margin: 20px;
        }}
        .info {{
            background: rgba(0, 243, 255, 0.1);
            border: 1px solid #00f3ff;
            padding: 10px;
            margin-top: 10px;
            color: #00f3ff;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        🔴 GLOBAL GORE NETWORK - STREAMING DIRECTO
    </div>
    
    <div class="video-container">
        <div class="loading" id="loading">
            🔄 Obteniendo stream...<br>
            <small>Esto puede tardar unos segundos</small>
        </div>
        
        <video id="videoPlayer" controls style="display: none;">
            Tu navegador no soporta video HTML5.
        </video>
        
        <div class="info" style="display: none;" id="info">
            📹 <strong>{title}</strong><br>
            🌐 Fuente: {url}
        </div>
        
        <div class="error" id="error" style="display: none;">
            ❌ Error al cargar el video<br>
            <small>El sitio puede estar bloqueado o el video no está disponible</small>
        </div>
    </div>
    
    <script>
        // Obtener URL de streaming via yt-dlp
        fetch('/global-gore/stream?url={urllib.parse.quote(url)}')
            .then(response => response.json())
            .then(data => {{
                const loading = document.getElementById('loading');
                const videoPlayer = document.getElementById('videoPlayer');
                const info = document.getElementById('info');
                const error = document.getElementById('error');
                
                loading.style.display = 'none';
                
                if (data.success && data.stream_url) {{
                    videoPlayer.src = data.stream_url;
                    videoPlayer.style.display = 'block';
                    info.style.display = 'block';
                    videoPlayer.play();
                }} else {{
                    error.style.display = 'block';
                    error.innerHTML = '❌ ' + (data.error || 'Error desconocido');
                }}
            }})
            .catch(err => {{
                document.getElementById('loading').style.display = 'none';
                document.getElementById('error').style.display = 'block';
            }});
    </script>
</body>
</html>"""
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(player_html.encode('utf-8'))
        
        # Global Gore: Obtener stream URL
        elif path.startswith('/global-gore/stream'):
            parsed = urllib.parse.urlparse(self.path)
            query = urllib.parse.parse_qs(parsed.query)
            
            url = query.get('url', [''])[0]
            url = urllib.parse.unquote(url)
            
            if not url:
                self.send_error(404, "URL no especificada")
                return
            
            try:
                # Usar yt-dlp para obtener URL directa del stream
                result = subprocess.run([
                    'yt-dlp',
                    '--get-url',
                    '-f', 'best',
                    url
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and result.stdout.strip():
                    stream_url = result.stdout.strip().split('\n')[0]
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    
                    response = {
                        'success': True,
                        'stream_url': stream_url
                    }
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                else:
                    raise Exception("No se pudo obtener URL de stream")
                    
            except Exception as e:
                print(f"❌ Error obteniendo stream: {str(e)}")
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    'success': False,
                    'error': str(e)
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
        
        else:
            self.send_error(404, "Ruta no encontrada")
    
    def do_POST(self):
        """Maneja peticiones POST"""
        global VIDEO_DATA, CURRENT_FILE
        
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        
        # Manejar subida de archivos (multipart/form-data)
        if path == '/admin/upload':
            try:
                content_type = self.headers.get('Content-Type', '')
                
                if 'multipart/form-data' not in content_type:
                    self.send_error(400, "Content-Type debe ser multipart/form-data")
                    return
                
                # Extraer boundary
                boundary = content_type.split('boundary=')[1].encode()
                
                # Leer todo el contenido
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                
                # Parsear multipart data manualmente
                parts = body.split(b'--' + boundary)
                
                for part in parts:
                    if b'Content-Disposition' in part and b'filename=' in part:
                        # Extraer nombre del archivo
                        filename_start = part.find(b'filename="') + 10
                        filename_end = part.find(b'"', filename_start)
                        filename = part[filename_start:filename_end].decode('utf-8')
                        
                        # Extraer contenido del archivo
                        file_data_start = part.find(b'\r\n\r\n') + 4
                        file_data_end = part.rfind(b'\r\n')
                        file_data = part[file_data_start:file_data_end]
                        
                        # Guardar archivo
                        if not os.path.exists(MEDIA_DIR):
                            os.makedirs(MEDIA_DIR)
                        
                        file_path = os.path.join(MEDIA_DIR, filename)
                        with open(file_path, 'wb') as f:
                            f.write(file_data)
                        
                        print(f"✅ Archivo subido: {filename} ({len(file_data)} bytes)")
                        
                        # Responder con éxito
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        
                        response = {
                            'success': True,
                            'filename': filename,
                            'size': len(file_data)
                        }
                        self.wfile.write(json.dumps(response).encode('utf-8'))
                        return
                
                self.send_error(400, "No se encontró archivo en la petición")
                
            except Exception as e:
                print(f"❌ Error en upload: {str(e)}")
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    'success': False,
                    'error': str(e)
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
            return
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        # Verificar clave de acceso
        if path == '/check-key':
            try:
                data = json.loads(body.decode('utf-8'))
                key = data.get('key', '').strip().upper()
                
                if key == ADMIN_KEY:
                    valid = True
                    admin = True
                    livegore = False
                    globalgore = False
                elif key == LIVEGORE_KEY:
                    valid = True
                    admin = False
                    livegore = True
                    globalgore = False
                elif key == GLOBAL_GORE_KEY:
                    valid = True
                    admin = False
                    livegore = False
                    globalgore = True
                else:
                    valid = key in VALID_KEYS
                    admin = False
                    livegore = False
                    globalgore = False
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {'valid': valid, 'admin': admin, 'livegore': livegore, 'globalgore': globalgore}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                self.send_error(400, f"Error: {str(e)}")
        
        # Verificar clave de descarga
        elif path == '/verify-download':
            try:
                data = json.loads(body.decode('utf-8'))
                key = data.get('key', '').strip().upper()
                
                valid = key == DOWNLOAD_KEY
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {'valid': valid}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                self.send_error(400, f"Error: {str(e)}")
        
        # Admin: Actualizar configuración
        elif path == '/admin/update-config':
            try:
                data = json.loads(body.decode('utf-8'))
                
                VIDEO_DATA = data.get('video_data', VIDEO_DATA)
                CURRENT_FILE = data.get('current_file', CURRENT_FILE)
                
                success = save_config()
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {'success': success}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
                if success:
                    print(f"✅ Configuración actualizada - Archivo activo: {CURRENT_FILE}")
                
            except Exception as e:
                self.send_error(400, f"Error: {str(e)}")
        
        # Admin: Descargar con YT-DLP
        elif path == '/admin/download-ytdlp':
            try:
                data = json.loads(body.decode('utf-8'))
                url = data.get('url', '').strip()
                
                if not url:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {'success': False, 'error': 'URL vacía'}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return
                
                if not os.path.exists(MEDIA_DIR):
                    os.makedirs(MEDIA_DIR)
                
                # Generar nombre de archivo único
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_template = os.path.join(MEDIA_DIR, f'ytdlp_{timestamp}_%(title)s.%(ext)s')
                
                print(f"📥 Descargando con yt-dlp: {url}")
                
                # Ejecutar yt-dlp con soporte para audio y video
                result = subprocess.run([
                    'yt-dlp',
                    '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    '--merge-output-format', 'mp4',
                    '--no-playlist',
                    '--extract-audio',  # Extraer audio si es necesario
                    '--audio-format', 'mp3',
                    '--audio-quality', '0',
                    '--embed-thumbnail',
                    '--add-metadata',
                    '-o', output_template,
                    url
                ], capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    # Buscar el archivo descargado
                    downloaded_files = [f for f in os.listdir(MEDIA_DIR) if f.startswith(f'ytdlp_{timestamp}')]
                    
                    if downloaded_files:
                        filename = downloaded_files[0]
                        file_path = os.path.join(MEDIA_DIR, filename)
                        file_size = os.path.getsize(file_path)
                        
                        print(f"✅ Descargado con yt-dlp: {filename}")
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        
                        response = {
                            'success': True,
                            'filename': filename,
                            'size': f"{file_size / 1024 / 1024:.2f} MB"
                        }
                        self.wfile.write(json.dumps(response).encode('utf-8'))
                    else:
                        raise Exception("No se encontró el archivo descargado")
                else:
                    raise Exception(result.stderr or "Error en yt-dlp")
                
            except subprocess.TimeoutExpired:
                print("❌ Timeout en yt-dlp")
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'success': False, 'error': 'Timeout: descarga muy larga'}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                print(f"❌ Error en yt-dlp: {str(e)}")
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'success': False, 'error': str(e)}
                self.wfile.write(json.dumps(response).encode('utf-8'))
        
        # Admin: Descargar con TikWM API
        elif path == '/admin/download-tikwm':
            try:
                data = json.loads(body.decode('utf-8'))
                url = data.get('url', '').strip()
                
                if not url:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {'success': False, 'error': 'URL vacía'}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return
                
                if not os.path.exists(MEDIA_DIR):
                    os.makedirs(MEDIA_DIR)
                
                print(f"📥 Descargando con TikWM: {url}")
                
                # Llamar a la API de TikWM
                api_url = "https://www.tikwm.com/api/"
                api_response = requests.post(api_url, json={'url': url}, timeout=30)
                api_data = api_response.json()
                
                if api_data.get('code') == 0:
                    video_data = api_data.get('data', {})
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    title = video_data.get('title', 'tiktok')[:50]
                    # Limpiar título
                    title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
                    
                    downloaded_files = []
                    
                    # Descargar video si existe
                    if 'play' in video_data or 'wmplay' in video_data:
                        video_url = video_data.get('play') or video_data.get('wmplay')
                        filename = f"tiktok_{timestamp}_{title}.mp4"
                        file_path = os.path.join(MEDIA_DIR, filename)
                        
                        video_content = requests.get(video_url, timeout=60)
                        with open(file_path, 'wb') as f:
                            f.write(video_content.content)
                        
                        downloaded_files.append(filename)
                        print(f"✅ Video descargado: {filename}")
                    
                    # Descargar imágenes si existen
                    if 'images' in video_data and video_data['images']:
                        for idx, img_url in enumerate(video_data['images']):
                            img_filename = f"tiktok_{timestamp}_{title}_img{idx+1}.jpg"
                            img_path = os.path.join(MEDIA_DIR, img_filename)
                            
                            img_content = requests.get(img_url, timeout=30)
                            with open(img_path, 'wb') as f:
                                f.write(img_content.content)
                            
                            downloaded_files.append(img_filename)
                            print(f"✅ Imagen descargada: {img_filename}")
                    
                    # Descargar audio si existe
                    if 'music' in video_data and video_data['music']:
                        music_url = video_data['music']
                        music_title = video_data.get('music_info', {}).get('title', title)
                        audio_filename = f"tiktok_{timestamp}_{music_title}_audio.mp3"
                        audio_path = os.path.join(MEDIA_DIR, audio_filename)
                        
                        try:
                            audio_content = requests.get(music_url, timeout=60)
                            with open(audio_path, 'wb') as f:
                                f.write(audio_content.content)
                            
                            downloaded_files.append(audio_filename)
                            print(f"✅ Audio descargado: {audio_filename}")
                        except:
                            pass  # El audio es opcional
                    
                    if downloaded_files:
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        
                        response = {
                            'success': True,
                            'filename': ', '.join(downloaded_files),
                            'type': 'multiple' if len(downloaded_files) > 1 else 'single',
                            'count': len(downloaded_files)
                        }
                        self.wfile.write(json.dumps(response).encode('utf-8'))
                    else:
                        raise Exception("No se descargó ningún archivo")
                else:
                    raise Exception(api_data.get('msg', 'Error en API de TikWM'))
                
            except Exception as e:
                print(f"❌ Error en TikWM: {str(e)}")
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'success': False, 'error': str(e)}
                self.wfile.write(json.dumps(response).encode('utf-8'))
        
        # Admin: Scraping de sitios gore
        elif path == '/admin/scrape-gore':
            try:
                data = json.loads(body.decode('utf-8'))
                site = data.get('site', '').strip()
                limit = int(data.get('limit', 10))
                include_uncensored = data.get('uncensored', True)
                include_censored = data.get('censored', False)
                
                if not site:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {'success': False, 'error': 'Sitio no especificado'}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return
                
                if not os.path.exists(MEDIA_DIR):
                    os.makedirs(MEDIA_DIR)
                
                print(f"🔴 Iniciando scraping de {site} (límite: {limit})")
                
                # Scraping según el sitio
                downloaded_files = []
                
                if site == 'kaotic':
                    downloaded_files = scrape_kaotic(limit, include_uncensored, include_censored)
                elif site == 'seegore':
                    downloaded_files = scrape_seegore(limit, include_uncensored, include_censored)
                elif site == 'theync':
                    downloaded_files = scrape_theync(limit, include_uncensored, include_censored)
                elif site == 'hoodsite':
                    downloaded_files = scrape_hoodsite(limit, include_uncensored, include_censored)
                else:
                    raise Exception(f"Sitio '{site}' no soportado")
                
                print(f"✅ Scraping completado: {len(downloaded_files)} archivos descargados")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    'success': True,
                    'downloaded': len(downloaded_files),
                    'total': limit,
                    'files': downloaded_files
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                print(f"❌ Error en scraping gore: {str(e)}")
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {'success': False, 'error': str(e)}
                self.wfile.write(json.dumps(response).encode('utf-8'))
        
        # Global Gore: Limpiar caché
        elif path == '/global-gore/clear-cache':
            try:
                global GLOBAL_GORE_CACHE
                GLOBAL_GORE_CACHE = {}
                
                print("🗑️ Caché de Global Gore limpiado")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {'success': True}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                print(f"❌ Error limpiando caché: {str(e)}")
                self.send_error(500, str(e))
        
        # Admin: Descargar desde URL
        elif path == '/admin/download-url':
            try:
                data = json.loads(body.decode('utf-8'))
                url = data.get('url', '').strip()
                
                if not url:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {'success': False, 'error': 'URL vacía'}
                    self.wfile.write(json.dumps(response).encode('utf-8'))
                    return
                
                # Obtener nombre del archivo desde URL
                filename = os.path.basename(urllib.parse.urlparse(url).path)
                if not filename:
                    filename = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
                
                # Crear directorio si no existe
                if not os.path.exists(MEDIA_DIR):
                    os.makedirs(MEDIA_DIR)
                
                file_path = os.path.join(MEDIA_DIR, filename)
                
                print(f"📥 Descargando desde: {url}")
                
                # Descargar archivo
                urllib.request.urlretrieve(url, file_path)
                
                file_size = os.path.getsize(file_path)
                print(f"✅ Descargado: {filename} ({file_size} bytes)")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    'success': True,
                    'filename': filename,
                    'size': file_size
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                print(f"❌ Error descargando URL: {str(e)}")
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                
                response = {
                    'success': False,
                    'error': str(e)
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
        
        else:
            self.send_error(404, "Endpoint no encontrado")

# ═══════════════════════════════════════════════════════════════
# ENDPOINTS ADICIONALES PARA LIVE GORE, YT-DLP Y TIKWM
# ═══════════════════════════════════════════════════════════════

def handle_livegore_content(handler):
    """Obtener contenido de Live Gore con paginación"""
    try:
        parsed = urllib.parse.urlparse(handler.path)
        query = urllib.parse.parse_qs(parsed.query)
        page = int(query.get('page', ['1'])[0])
        limit = int(query.get('limit', ['12'])[0])
        
        # Obtener todos los archivos
        all_files = []
        if os.path.exists(MEDIA_DIR):
            for filename in os.listdir(MEDIA_DIR):
                file_path = os.path.join(MEDIA_DIR, filename)
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    ext = os.path.splitext(filename)[1].lower()
                    
                    # Determinar tipo
                    if ext in ['.mp4', '.avi', '.mkv', '.mov', '.webm']:
                        file_type = 'video'
                    elif ext in ['.mp3', '.wav', '.ogg', '.m4a']:
                        file_type = 'audio'
                    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                        file_type = 'image'
                    else:
                        file_type = 'other'
                    
                    all_files.append({
                        'filename': filename,
                        'title': os.path.splitext(filename)[0],
                        'size': f"{size / 1024 / 1024:.2f} MB",
                        'date': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d'),
                        'type': file_type
                    })
        
        # Ordenar por fecha (más reciente primero)
        all_files.sort(key=lambda x: x['date'], reverse=True)
        
        # Paginación
        total = len(all_files)
        total_pages = (total + limit - 1) // limit
        start = (page - 1) * limit
        end = start + limit
        
        items = all_files[start:end]
        
        handler.send_response(200)
        handler.send_header('Content-type', 'application/json')
        handler.end_headers()
        
        response = {
            'items': items,
            'page': page,
            'totalPages': total_pages,
            'total': total
        }
        handler.wfile.write(json.dumps(response).encode('utf-8'))
        
    except Exception as e:
        print(f"❌ Error en livegore content: {str(e)}")
        handler.send_error(500, str(e))

def handle_livegore_play(handler):
    """Reproducir contenido de Live Gore"""
    try:
        parsed = urllib.parse.urlparse(handler.path)
        query = urllib.parse.parse_qs(parsed.query)
        filename = query.get('file', [''])[0]
        
        if not filename:
            handler.send_error(404, "Archivo no especificado")
            return
        
        file_path = os.path.join(MEDIA_DIR, filename)
        if not os.path.exists(file_path):
            handler.send_error(404, "Archivo no encontrado")
            return
        
        # HTML del reproductor
        content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        
        if content_type.startswith('video'):
            player_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>▶ {filename}</title>
    <style>
        body {{
            margin: 0;
            background: #000;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        video {{
            max-width: 100%;
            max-height: 100vh;
        }}
    </style>
</head>
<body>
    <video controls autoplay>
        <source src="/livegore/stream?file={urllib.parse.quote(filename)}" type="{content_type}">
        Tu navegador no soporta video HTML5.
    </video>
</body>
</html>"""
        elif content_type.startswith('audio'):
            player_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>🎵 {filename}</title>
    <style>
        body {{
            margin: 0;
            background: #0a0a0a;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            font-family: 'Courier New', monospace;
            color: #00f3ff;
        }}
        .container {{
            text-align: center;
        }}
        audio {{
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>🎵 {filename}</h2>
        <audio controls autoplay>
            <source src="/livegore/stream?file={urllib.parse.quote(filename)}" type="{content_type}">
            Tu navegador no soporta audio HTML5.
        </audio>
    </div>
</body>
</html>"""
        elif content_type.startswith('image'):
            player_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>🖼️ {filename}</title>
    <style>
        body {{
            margin: 0;
            background: #000;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        img {{
            max-width: 100%;
            max-height: 100vh;
        }}
    </style>
</head>
<body>
    <img src="/livegore/stream?file={urllib.parse.quote(filename)}" alt="{filename}">
</body>
</html>"""
        else:
            handler.send_error(415, "Tipo de archivo no soportado")
            return
        
        handler.send_response(200)
        handler.send_header('Content-type', 'text/html; charset=utf-8')
        handler.end_headers()
        handler.wfile.write(player_html.encode('utf-8'))
        
    except Exception as e:
        print(f"❌ Error en livegore play: {str(e)}")
        handler.send_error(500, str(e))

def handle_livegore_stream(handler):
    """Stream del archivo de Live Gore"""
    try:
        parsed = urllib.parse.urlparse(handler.path)
        query = urllib.parse.parse_qs(parsed.query)
        filename = query.get('file', [''])[0]
        
        if not filename:
            handler.send_error(404, "Archivo no especificado")
            return
        
        file_path = os.path.join(MEDIA_DIR, filename)
        if not os.path.exists(file_path):
            handler.send_error(404, "Archivo no encontrado")
            return
        
        handler.send_response(200)
        content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        handler.send_header('Content-type', content_type)
        handler.end_headers()
        
        with open(file_path, 'rb') as f:
            handler.wfile.write(f.read())
        
    except Exception as e:
        print(f"❌ Error en livegore stream: {str(e)}")
        handler.send_error(500, str(e))

# Modificar la clase DarkNeonHandler para incluir los nuevos endpoints

# ═══════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ═══════════════════════════════════════════════════════════════

def main():
    # Cargar configuración existente
    load_config()
    
    # Crear carpeta de media si no existe
    if not os.path.exists(MEDIA_DIR):
        os.makedirs(MEDIA_DIR)
        print(f"✓ Carpeta '{MEDIA_DIR}' creada")
    
    # Iniciar servidor
    server = HTTPServer(('0.0.0.0', PORT), DarkNeonHandler)
    
    print("\n" + "═" * 70)
    print("🎬 DARK NEON VIDEO SERVER - GORE EDITION")
    print("═" * 70)
    print(f"🌐 Servidor: http://localhost:{PORT}")
    print(f"📁 Archivos: {MEDIA_DIR}/")
    print(f"🔑 Claves usuario: {', '.join(VALID_KEYS)}")
    print(f"🔧 Clave ADMIN: {ADMIN_KEY}")
    print(f"🔴 Clave LIVE GORE: {LIVEGORE_KEY}")
    print(f"🌐 Clave GLOBAL GORE: {GLOBAL_GORE_KEY}")
    print(f"⬇️  Clave DESCARGA: {DOWNLOAD_KEY}")
    print("\n💡 Características:")
    print("   ✓ Panel de administración completo")
    print("   ✓ Live Gore Gallery (contenido descargado)")
    print("   ✓ 🌐 GLOBAL GORE NETWORK (streaming directo)")
    print("   ✓ Scraper automático de sitios gore")
    print("   ✓ Subida de archivos desde dispositivo")
    print("   ✓ Descarga con YT-DLP (YouTube, Instagram, etc.)")
    print("   ✓ Descarga con TikWM (TikTok - video, foto, audio)")
    print("   ✓ Descarga directa desde URL")
    print("\n🎮 Instrucciones:")
    print("   1. Acceso normal: usa DEMO2026, TERROR o NEON")
    print("   2. Acceso admin: usa INTEGER")
    print("   3. Acceso Live Gore (descargados): usa NOA999")
    print("   4. Acceso Global Gore (streaming): usa NOA666")
    print("   5. Descarga archivos: usa NOA")
    print("\n🌐 Global Gore Network (NOA666):")
    print("   - Videos de Kaotic, SeeGore, TheYNC, HoodSite")
    print("   - Streaming directo sin descargar")
    print("   - Contenido actualizado en tiempo real")
    print("   - Miles de videos disponibles")
    print("\n📦 Dependencias requeridas:")
    print("   - yt-dlp: pip install yt-dlp")
    print("   - requests: pip install requests")
    print("   - beautifulsoup4: pip install beautifulsoup4")
    print("\n⏹️  Presiona Ctrl+C para detener")
    print("═" * 70 + "\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido")
        server.shutdown()

if __name__ == '__main__':
    main()
