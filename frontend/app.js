/**
 * Competitor Monitor - Frontend Application
 */

// === State ===
const state = {
    currentTab: 'text',
    selectedImage: null,
    selectedPdf: null, // Добавлено для PDF
    isLoading: false
};

// === DOM Elements ===
const elements = {
    navButtons: document.querySelectorAll('.nav-btn'),
    tabContents: document.querySelectorAll('.tab-content'),
    
    // Text analysis
    competitorText: document.getElementById('raw-text'), // Исправлено под твой HTML
    analyzeTextBtn: document.getElementById('analyze-text-btn'),
    
    // PDF analysis (Добавлено)
    pdfInput: document.getElementById('pdf-input'),
    analyzePdfBtn: document.getElementById('analyze-pdf-btn'),
    pdfPreview: document.getElementById('pdf-preview'),
    pdfName: document.getElementById('pdf-name'),

    // Image analysis
    uploadZone: document.getElementById('image-upload-zone'), // Исправлено под твой HTML
    imageInput: document.getElementById('image-input'),
    previewContainer: document.getElementById('image-preview'),
    imagePreview: document.getElementById('preview-img'),
    analyzeImageBtn: document.getElementById('analyze-image-btn'),
    
    // Parse demo
    parseBtn: document.getElementById('run-parse-demo'),
    
    // History
    historyList: document.getElementById('history-list'),
    
    // Results
    resultsSection: document.getElementById('results-area'),
    resultsContent: document.getElementById('analysis-results'),
    
    // Loading
    loadingOverlay: document.getElementById('loading-overlay')
};

// === API Functions ===
const api = {
    baseUrl: '',
    
    async analyzeText(text) {
        // Исправлено: analyze-text вместо analyze_text
        const response = await fetch(`${this.baseUrl}/analyze-text`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        return response.json();
    },

    async analyzePdf(file) {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch(`${this.baseUrl}/analyze-pdf`, {
            method: 'POST',
            body: formData
        });
        return response.json();
    },
    
    async analyzeImage(file) {
        const formData = new FormData();
        formData.append('file', file);
        const response = await fetch(`${this.baseUrl}/analyze-image`, {
            method: 'POST',
            body: formData
        });
        return response.json();
    },
    
    async parseDemo() {
        const response = await fetch(`${this.baseUrl}/parsedemo`);
        return response.json();
    },
    
    async getHistory() {
        const response = await fetch(`${this.baseUrl}/get-history`);
        return response.json();
    }
};

// === UI Functions ===
const ui = {
    showLoading() {
        elements.loadingOverlay.style.display = 'flex';
    },
    
    hideLoading() {
        elements.loadingOverlay.style.display = 'none';
    },
    
    showTab(tabId) {
        state.currentTab = tabId;
        elements.navButtons.forEach(btn => btn.classList.toggle('active', btn.dataset.tab === tabId));
        elements.tabContents.forEach(content => content.classList.toggle('active', content.id === tabId));
        if (tabId === 'history-tab') this.loadHistory();
    },
    
    showResults(content) {
        // Умный вывод: если пришел объект (анализ), форматируем его. Если строка — выводим как есть.
        let html = '';
        if (typeof content === 'object') {
            html = this.renderAnalysisObject(content);
        } else {
            html = `<p>${content.replace(/\n/g, '<br>')}</p>`;
        }
        
        elements.resultsContent.innerHTML = html;
        elements.resultsSection.hidden = false;
        elements.resultsSection.scrollIntoView({ behavior: 'smooth' });
    },

    renderAnalysisObject(analysis) {
        // Позволяет выводить данные, даже если они вложены в объект 'analysis'
        const data = analysis.analysis || analysis; 
        return `
            <div class="result-block">
                <h3>Результат анализа</h3>
                <p>${(data.summary || data).replace(/\n/g, '<br>')}</p>
            </div>
        `;
    },

    async loadHistory() {
        try {
            const data = await api.getHistory();
            elements.historyList.innerHTML = data.map(item => `
                <div class="history-item" style="border-bottom: 1px solid #eee; padding: 10px;">
                    <strong>${item.request_type}</strong>: ${item.request_summary}
                </div>
            `).join('');
        } catch (e) {
            elements.historyList.innerHTML = "Ошибка загрузки истории";
        }
    }
};

// === Event Handlers ===
const handlers = {
    async handleAnalyzeText() {
        const text = elements.competitorText.value.trim();
        if (!text) return alert('Введите текст');
        ui.showLoading();
        try {
            const result = await api.analyzeText(text);
            ui.showResults(result.analysis);
        } catch (e) { alert('Ошибка соединения'); }
        ui.hideLoading();
    },

    handlePdfSelect(e) {
        const file = e.target.files[0];
        if (file) {
            state.selectedPdf = file;
            elements.pdfName.innerText = file.name;
            elements.pdfPreview.hidden = false;
            elements.analyzePdfBtn.disabled = false;
        }
    },

    async handleAnalyzePdf() {
        if (!state.selectedPdf) return;
        ui.showLoading();
        try {
            const result = await api.analyzePdf(state.selectedPdf);
            ui.showResults(result.analysis);
        } catch (e) { alert('Ошибка PDF'); }
        ui.hideLoading();
    },

    handleImageSelect(e) {
        const file = e.target.files[0];
        if (file) {
            state.selectedImage = file;
            const reader = new FileReader();
            reader.onload = (ev) => {
                elements.imagePreview.src = ev.target.result;
                elements.previewContainer.hidden = false;
                elements.analyzeImageBtn.disabled = false;
            };
            reader.readAsDataURL(file);
        }
    },

    async handleAnalyzeImage() {
        if (!state.selectedImage) return;
        ui.showLoading();
        try {
            const result = await api.analyzeImage(state.selectedImage);
            ui.showResults(result.analysis);
        } catch (e) { alert('Ошибка фото'); }
        ui.hideLoading();
    },

    async handleParse() {
        ui.showLoading();
        try {
            const result = await api.parseDemo();
            ui.showResults(result.analysis);
        } catch (e) { alert('Ошибка парсинга'); }
        ui.hideLoading();
    }
};

// === Initialize ===
function init() {
    elements.navButtons.forEach(btn => btn.addEventListener('click', (e) => ui.showTab(e.target.dataset.tab)));
    elements.analyzeTextBtn?.addEventListener('click', handlers.handleAnalyzeText);
    
    // PDF
    elements.pdfInput?.addEventListener('change', handlers.handlePdfSelect);
    elements.analyzePdfBtn?.addEventListener('click', handlers.handleAnalyzePdf);

    // Image
    elements.imageInput?.addEventListener('change', handlers.handleImageSelect);
    elements.analyzeImageBtn?.addEventListener('click', handlers.handleAnalyzeImage);

    // Parse
    elements.parseBtn?.addEventListener('click', handlers.handleParse);

    ui.showTab('content-tab');
}

document.addEventListener('DOMContentLoaded', init);