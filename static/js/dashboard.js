document.addEventListener('DOMContentLoaded', function () {
    loadHistory();

    // URL Scan Handler
    document.getElementById('urlScanBtn').addEventListener('click', function () {
        const urlInput = document.getElementById('urlInput');
        const url = urlInput.value.trim();

        if (!url) return;

        const btn = this;
        const originalText = btn.innerHTML;
        const resultArea = document.getElementById('urlResult');

        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Scanning...';

        fetch('/predict_url', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: url })
        })
            .then(response => response.json())
            .then(data => {
                let badgeClass = data.prediction === 'Phishing' ? 'badge-phishing' : 'badge-safe';
                let icon = data.prediction === 'Phishing' ? '⚠️' : '✅';

                resultArea.innerHTML = `
                <div class="alert ${data.prediction === 'Phishing' ? 'alert-danger' : 'alert-success'} mt-3 border-0" style="background-color: rgba(${data.prediction === 'Phishing' ? '239, 68, 68' : '34, 197, 94'}, 0.2); color: white;">
                    <h5>${icon} Scan Result: <strong>${data.prediction}</strong></h5>
                    <p class="mb-0">Target: ${data.url}</p>
                </div>
            `;
                loadHistory(); // Refresh history
            })
            .catch(error => {
                console.error('Error:', error);
                resultArea.innerHTML = '<div class="alert alert-warning mt-3">Error performing scan.</div>';
            })
            .finally(() => {
                btn.disabled = false;
                btn.innerHTML = originalText;
            });
    });
});

function loadHistory() {
    fetch('/api/history')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('historyList');
            if (data.length === 0) {
                container.innerHTML = '<div class="text-center text-muted p-3">No recent activity</div>';
                return;
            }

            let html = '';
            data.forEach(item => {
                let badgeClass = 'badge-secondary';
                if (item.prediction === 'Phishing') badgeClass = 'badge-phishing';
                if (item.prediction === 'Legitimate') badgeClass = 'badge-safe';
                if (item.prediction === 'Batch Analysis') badgeClass = 'badge-info';

                const date = new Date(item.timestamp).toLocaleString();

                html += `
                    <div class="history-item">
                        <div>
                            <div class="fw-bold">${item.name}</div>
                            <div class="small text-secondary">${date}</div>
                        </div>
                        <span class="badge ${badgeClass} rounded-pill px-3 py-2">${item.prediction}</span>
                    </div>
                `;
            });
            container.innerHTML = html;
        });
}
