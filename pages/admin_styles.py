"""Admin dashboard styles for MSME CPMS"""

# Global styles for clean admin dashboard
GLOBAL_STYLES = """
<style>
:root {
    --primary: #172087;
    --primary-dark: #1e3a8a;
    --bg: #f8fafc;
    --text: #374151;
    --border: #e5e7eb;
    --shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.main .block-container {
    max-width: 1200px;
    margin: 0 auto !important;
    padding: 60px 2rem 2rem !important;
}

.stApp { background-color: var(--bg) !important; }
#MainMenu, footer, .stDeployButton { display: none !important; }

header[data-testid="stHeader"] {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    height: 50px !important;
    background: linear-gradient(90deg, var(--primary) 0%, var(--primary-dark) 50%, var(--primary) 100%) !important;
    z-index: 999999 !important;
    display: flex !important;
    align-items: center !important;
}

/* Data table styles */
.data-table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 8px;
    box-shadow: var(--shadow);
}

.data-table th {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    color: white;
    padding: 12px;
    text-align: left;
    font-weight: 600;
}

.data-table td {
    padding: 12px;
    border-bottom: 1px solid var(--border);
    vertical-align: top;
    font-size: 13px;
    line-height: 1.4;
}

.data-table tr:hover { background-color: #f9fafb; }
.data-table tr:last-child td { border-bottom: none; }

/* Status indicators */
.status-approved {
    background: #dcfce7;
    color: #166534;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
}

.status-pending {
    background: #fef3c7;
    color: #92400e;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
}

.status-online {
    background: #dcfce7;
    color: #166534;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
}

.status-offline {
    background: #f3f4f6;
    color: #374151;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
}

.admin-info-value {
    color: #0369a1;
    font-family: "Courier New", monospace;
    background: rgba(255,255,255,0.7);
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
}

/* Responsive styles */
@media (max-width: 768px) {
    .nav-menu { flex-direction: column; }
    .nav-item { min-width: 100%; }
    .content-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 1rem;
    }
    .metrics-grid { grid-template-columns: 1fr; }
}

/* Footer styles */
.footer-content {
    margin-top: 3rem;
    padding-top: 2rem;
    border-top: 1px solid var(--border);
    text-align: center;
}

.footer-text {
    color: #6b7280;
    font-size: 0.875rem;
}

.copyright {
    margin-top: 0.5rem;
    font-size: 0.75rem;
    color: #9ca3af;
}

/* Custom scrollbar */
::-webkit-scrollbar { width: 8px; }
::-webkit-scrollbar-track { background: #f1f5f9; }
::-webkit-scrollbar-thumb {
    background: #172087;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover { background: #1e40af; }
</style>
"""