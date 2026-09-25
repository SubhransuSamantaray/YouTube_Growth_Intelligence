/**
 * YouTube Growth Intelligence Platform - Neural Client Application v2.0
 * Ultra-interactive, futuristic cyber HUD client with real-time title analyzer,
 * timeline scrubbing radar, 90-day compounding scenario planner, command palette,
 * and evidence popovers.
 */

let isBrutalMode = false;
let currentTab = 'dashboard';
let charts = {};
let currentVideosData = [];
let allEvidenceStore = {};
let selectedRetentionVideoId = null;

document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

async function initApp() {
    initGlobalShortcuts();
    await loadDashboard();
    await loadComplianceHeader();
    initTitleAnalyzer();
    initCompoundingScenarioPlanner();
    loadBenchmarkTab();
    lucide.createIcons();
}

// =========================================================================
// GLOBAL SHORTCUTS & COMMAND PALETTE (CTRL + K)
// =========================================================================
function initGlobalShortcuts() {
    window.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
            e.preventDefault();
            openCommandPalette();
        } else if (e.key === 'Escape') {
            closeCommandPalette();
            closeDrilldownModal();
            closeEvidenceModal();
        }
    });

    const backdrop = document.getElementById('command-palette-backdrop');
    if (backdrop) {
        backdrop.addEventListener('click', (e) => {
            if (e.target === backdrop) closeCommandPalette();
        });
    }
}

function openCommandPalette() {
    const backdrop = document.getElementById('command-palette-backdrop');
    const input = document.getElementById('cmd-palette-input');
    if (backdrop && input) {
        backdrop.classList.remove('hidden');
        input.value = '';
        input.focus();
        filterCommandPalette('');
    }
}

function closeCommandPalette() {
    const backdrop = document.getElementById('command-palette-backdrop');
    if (backdrop) backdrop.classList.add('hidden');
}

function filterCommandPalette(query) {
    const container = document.getElementById('cmd-palette-results');
    if (!container) return;

    const q = query.toLowerCase().trim();
    const defaultActions = [
        { label: 'Executive HUD Overview', icon: 'layout-dashboard', action: () => switchTab('dashboard') },
        { label: 'Videos & Performance Scorecards', icon: 'video', action: () => switchTab('videos') },
        { label: 'Audience Retention Radar & Hooks', icon: 'activity', action: () => switchTab('retention') },
        { label: 'Pre-Publish Neural Simulator', icon: 'bot', action: () => switchTab('predictions') },
        { label: '90-Day Compounding Growth Planner', icon: 'trending-up', action: () => switchTab('scenario') },
        { label: 'Strategic Evidence-Grounded Recommendations', icon: 'lightbulb', action: () => switchTab('recommendations') },
        { label: 'Layman Growth Academy (Plain English Guide)', icon: 'sparkles', action: () => switchTab('layman') },
        { label: 'Ecosystem Teardown & Benchmarks', icon: 'scale', action: () => switchTab('benchmark') },
        { label: 'Toggle Brutal Analysis Mode', icon: 'zap', action: () => toggleBrutalMode() },
        { label: 'Download Executive PDF Dossier', icon: 'file-down', action: () => downloadReport('pdf') },
        { label: 'Run 30-Day Policy TTL Sweeper', icon: 'trash-2', action: () => triggerTtlSweep() }
    ];

    let items = defaultActions.filter(a => !q || a.label.toLowerCase().includes(q));

    // Also match video titles if videos are loaded
    if (q && currentVideosData.length > 0) {
        const matchingVideos = currentVideosData
            .filter(v => v.title.toLowerCase().includes(q))
            .slice(0, 5)
            .map(v => ({
                label: `Inspect: ${v.title}`,
                icon: 'play-circle',
                action: () => {
                    closeCommandPalette();
                    openVideoDrilldown(v.video_id);
                }
            }));
        items = [...items, ...matchingVideos];
    }

    if (items.length === 0) {
        container.innerHTML = `<div class="p-4 text-center text-xs text-slate-500">No matching commands or videos found.</div>`;
        return;
    }

    container.innerHTML = items.map((item, idx) => `
        <div class="cmd-item" onclick="executeCmdItem(${idx})">
            <div class="flex items-center space-x-2.5">
                <i data-lucide="${item.icon}" class="w-4 h-4 text-cyan-400"></i>
                <span>${item.label}</span>
            </div>
            <kbd class="text-[10px] text-slate-500 font-mono">↵</kbd>
        </div>
    `).join('');

    // Store callbacks on container
    container._actions = items.map(i => i.action);
    lucide.createIcons();
}

function executeCmdItem(index) {
    const container = document.getElementById('cmd-palette-results');
    if (container && container._actions && container._actions[index]) {
        container._actions[index]();
        closeCommandPalette();
    }
}

// Toast Notifications
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'cyber-toast';
    const iconName = type === 'success' ? 'check-circle' : (type === 'warning' ? 'alert-triangle' : 'info');
    const colorClass = type === 'success' ? 'text-emerald-400' : (type === 'warning' ? 'text-rose-400' : 'text-cyan-400');

    toast.innerHTML = `
        <i data-lucide="${iconName}" class="w-4 h-4 ${colorClass} shrink-0"></i>
        <span>${message}</span>
    `;
    container.appendChild(toast);
    lucide.createIcons();

    setTimeout(() => {
        toast.style.transition = 'opacity 0.3s, transform 0.3s';
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// =========================================================================
// NAVIGATION & THEME TOGGLES
// =========================================================================
function switchTab(tabId) {
    currentTab = tabId;
    
    // Update nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
    const activeNav = document.getElementById(`nav-${tabId}`);
    if (activeNav) activeNav.classList.add('active');

    // Hide all sections
    document.querySelectorAll('main > section').forEach(sec => sec.classList.add('hidden'));
    
    // Show target section
    const target = document.getElementById(`tab-${tabId}`);
    if (target) {
        target.classList.remove('hidden');
    }

    // Trigger tab-specific loader
    if (tabId === 'dashboard') loadDashboard();
    else if (tabId === 'videos') loadVideosTable();
    else if (tabId === 'retention') loadRetentionTab();
    else if (tabId === 'traffic') loadTrafficTab();
    else if (tabId === 'audience') loadAudienceTab();
    else if (tabId === 'content-intelligence') loadContentIntelligenceTab();
    else if (tabId === 'scenario') updateScenarioPlanner();
    else if (tabId === 'growth') loadGrowthMatrix();
    else if (tabId === 'predictions') runSimulation();
    else if (tabId === 'recommendations') loadRecommendations();
    else if (tabId === 'reports') updateReportsView();
    else if (tabId === 'data-sources') loadComplianceTab();
    else if (tabId === 'model-center') loadModelCenter();
    else if (tabId === 'benchmark') loadBenchmarkTab();
    else if (tabId === 'layman') showToast('Layman Growth Academy Loaded: Zero-Jargon Plain English Active!', 'info');

    setTimeout(() => lucide.createIcons(), 50);
}

let isEli5Mode = false;

function toggleEli5Mode() {
    isEli5Mode = !isEli5Mode;
    const btn = document.getElementById('eli5-mode-btn');
    const label = document.getElementById('eli5-btn-label');
    
    if (isEli5Mode) {
        if (btn) {
            btn.classList.add('bg-amber-500/30', 'border-amber-400');
            btn.classList.remove('bg-amber-500/10');
        }
        if (label) label.innerText = 'Plain English (Active)';
        showToast('Plain English Mode Activated: Zero-Jargon Explanations Enabled!', 'info');
        switchTab('layman');
    } else {
        if (btn) {
            btn.classList.remove('bg-amber-500/30', 'border-amber-400');
            btn.classList.add('bg-amber-500/10');
        }
        if (label) label.innerText = 'Plain English (ELI5)';
        showToast('Technical Mode Restored', 'info');
        switchTab('dashboard');
    }
}

function toggleBrutalMode() {
    const toggle = document.getElementById('brutal-mode-toggle');
    if (!toggle) return;
    isBrutalMode = toggle.checked;
    
    // Shift theme class on body
    document.body.classList.toggle('brutal-active', isBrutalMode);

    // Show/hide alert banner
    const banner = document.getElementById('brutal-alert-banner');
    if (banner) {
        if (isBrutalMode) banner.classList.remove('hidden');
        else banner.classList.add('hidden');
    }

    // Notification
    if (isBrutalMode) {
        showToast('Brutal Diagnostic Mode Activated: Direct algorithmic critiques enabled', 'warning');
    } else {
        showToast('Standard Executive Mode Restored', 'info');
    }

    // Update Report title
    const reportTitle = document.getElementById('report-preview-title');
    if (reportTitle) {
        reportTitle.innerText = isBrutalMode 
            ? 'Executive Channel Growth Report (BRUTAL STRATEGIC AUDIT MODE)' 
            : 'Executive Channel Growth Report (Standard Mode)';
    }

    // Refresh affected views
    if (currentTab === 'recommendations') loadRecommendations();
    else if (currentTab === 'growth') loadGrowthMatrix();
    else if (currentTab === 'reports') updateReportsView();
}

// =========================================================================
// TAB 1: EXECUTIVE HUD DASHBOARD
// =========================================================================
async function loadDashboard() {
    try {
        const res = await fetch('/api/v1/summary');
        const data = await res.json();
        if (data.error) return;

        document.getElementById('top-channel-name').innerText = data.channel_name;

        // Render KPI Cards
        const grid = document.getElementById('kpi-cards-grid');
        grid.innerHTML = `
            <div class="glass-card p-4 shadow-sm group hover:border-cyan-500/40 transition">
                <div class="flex items-center justify-between text-xs text-slate-400">
                    <span class="font-medium">Total Views</span>
                    <i data-lucide="eye" class="w-4 h-4 text-cyan-400 group-hover:scale-110 transition"></i>
                </div>
                <div class="text-2xl font-black text-white mt-1 tracking-tight">${data.total_views.toLocaleString()}</div>
                <div class="text-[11px] text-emerald-400 mt-1 flex items-center space-x-1">
                    <i data-lucide="trending-up" class="w-3 h-3"></i>
                    <span>${data.total_videos} uploads analyzed</span>
                </div>
            </div>

            <div class="glass-card p-4 shadow-sm group hover:border-emerald-500/40 transition">
                <div class="flex items-center justify-between text-xs text-slate-400">
                    <span class="font-medium">Total Watch Time</span>
                    <i data-lucide="clock" class="w-4 h-4 text-emerald-400 group-hover:scale-110 transition"></i>
                </div>
                <div class="text-2xl font-black text-white mt-1 tracking-tight">${data.total_watch_time_hrs.toLocaleString()} <span class="text-xs font-semibold text-slate-400">hrs</span></div>
                <div class="text-[11px] text-slate-400 mt-1">Avg ${Math.round(data.avg_view_duration_sec)}s per view</div>
            </div>

            <div class="glass-card p-4 shadow-sm group hover:border-purple-500/40 transition">
                <div class="flex items-center justify-between text-xs text-slate-400">
                    <span class="font-medium">Net Subscribers</span>
                    <i data-lucide="user-plus" class="w-4 h-4 text-purple-400 group-hover:scale-110 transition"></i>
                </div>
                <div class="text-2xl font-black text-white mt-1 tracking-tight">+${data.total_subscribers.toLocaleString()}</div>
                <div class="text-[11px] text-purple-300 mt-1 flex items-center space-x-1">
                    <i data-lucide="award" class="w-3 h-3"></i>
                    <span>+5.5 subs / 1k views</span>
                </div>
            </div>

            <div class="glass-card p-4 shadow-sm group hover:border-amber-500/40 transition">
                <div class="flex items-center justify-between text-xs text-slate-400">
                    <span class="font-medium">Avg Audience Retention</span>
                    <i data-lucide="activity" class="w-4 h-4 text-amber-400 group-hover:scale-110 transition"></i>
                </div>
                <div class="text-2xl font-black text-white mt-1 tracking-tight">${data.avg_view_percentage}%</div>
                <div class="text-[11px] text-slate-400 mt-1">Top format: ${data.top_format}</div>
            </div>
        `;

        // Load videos for charts
        const vRes = await fetch('/api/v1/videos?sort_by=total_views&order=desc');
        const videos = await vRes.json();
        currentVideosData = videos;

        renderDashboardCharts(videos);
        loadCohortCharts();
        lucide.createIcons();

    } catch (err) {
        console.error('Failed to load dashboard:', err);
    }
}

function renderDashboardCharts(videos) {
    const top10 = videos.slice(0, 10);
    const labels = top10.map(v => v.title.length > 25 ? v.title.substring(0, 22) + '...' : v.title);
    const views = top10.map(v => v.total_views);
    const watchHours = top10.map(v => v.total_watch_time_hrs);

    // Bar Chart
    const ctxBar = document.getElementById('chart-dashboard-views').getContext('2d');
    if (charts.dashViews) charts.dashViews.destroy();
    charts.dashViews = new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Views',
                    data: views,
                    backgroundColor: 'rgba(56, 189, 248, 0.85)',
                    borderRadius: 6,
                    yAxisID: 'y'
                },
                {
                    label: 'Watch Time (Hrs)',
                    data: watchHours,
                    backgroundColor: 'rgba(16, 185, 129, 0.85)',
                    borderRadius: 6,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            scales: {
                x: {
                    ticks: { color: '#94a3b8', font: { size: 10 } },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                },
                y: {
                    type: 'linear',
                    position: 'left',
                    ticks: { color: '#38bdf8', font: { size: 10 } },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                },
                y1: {
                    type: 'linear',
                    position: 'right',
                    ticks: { color: '#34d399', font: { size: 10 } },
                    grid: { drawOnChartArea: false }
                }
            },
            plugins: {
                legend: { labels: { color: '#cbd5e1', font: { size: 11 } } }
            }
        }
    });

    // Doughnut Chart (Performance Tiers)
    const tierCounts = { 'Viral Breakout': 0, 'Above Average': 0, 'Average': 0, 'Underperforming': 0 };
    videos.forEach(v => {
        if (tierCounts[v.performance_tier] !== undefined) tierCounts[v.performance_tier]++;
        else tierCounts['Average']++;
    });

    const ctxDoughnut = document.getElementById('chart-dashboard-tiers').getContext('2d');
    if (charts.dashTiers) charts.dashTiers.destroy();
    charts.dashTiers = new Chart(ctxDoughnut, {
        type: 'doughnut',
        data: {
            labels: Object.keys(tierCounts),
            datasets: [{
                data: Object.values(tierCounts),
                backgroundColor: [
                    'rgba(56, 189, 248, 0.9)',
                    'rgba(16, 185, 129, 0.9)',
                    'rgba(99, 102, 241, 0.9)',
                    'rgba(244, 63, 94, 0.9)'
                ],
                borderColor: '#0f172a',
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#cbd5e1', font: { size: 10 }, boxWidth: 12 } }
            }
        }
    });
}

async function loadCohortCharts() {
    try {
        const res = await fetch('/api/v1/cohorts');
        const data = await res.json();

        // Day Cohort Chart
        const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
        const dayMedians = days.map(d => data.by_day_of_week[d]?.median_views || 0);

        const ctxDay = document.getElementById('chart-cohort-day').getContext('2d');
        if (charts.cohortDay) charts.cohortDay.destroy();
        charts.cohortDay = new Chart(ctxDay, {
            type: 'bar',
            data: {
                labels: days.map(d => d.substring(0, 3)),
                datasets: [{
                    label: 'Median Views',
                    data: dayMedians,
                    backgroundColor: 'rgba(56, 189, 248, 0.8)',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                    y: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
                },
                plugins: { legend: { display: false } }
            }
        });

        // Duration Cohort Chart
        const formats = ['Short', 'Mid-form', 'Deep Dive'];
        const formatRetention = formats.map(f => data.by_duration_bucket[f]?.avg_view_pct || 0);

        const ctxDur = document.getElementById('chart-cohort-duration').getContext('2d');
        if (charts.cohortDur) charts.cohortDur.destroy();
        charts.cohortDur = new Chart(ctxDur, {
            type: 'bar',
            data: {
                labels: formats,
                datasets: [{
                    label: 'Avg Retention %',
                    data: formatRetention,
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                    y: { max: 100, ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
                },
                plugins: { legend: { display: false } }
            }
        });
    } catch (err) {
        console.error('Failed to load cohorts:', err);
    }
}

// =========================================================================
// TAB 2: VIDEOS & SCORECARDS
// =========================================================================
async function loadVideosTable() {
    const fmt = document.getElementById('filter-video-format').value;
    const tier = document.getElementById('filter-video-tier').value;

    const res = await fetch(`/api/v1/videos?format_type=${fmt}&performance_tier=${tier}`);
    const videos = await res.json();
    currentVideosData = videos;
    renderVideosTableList(videos);
}

function filterVideosLive() {
    const q = document.getElementById('video-search-input').value.toLowerCase().trim();
    if (!q) {
        renderVideosTableList(currentVideosData);
        return;
    }
    const filtered = currentVideosData.filter(v => v.title.toLowerCase().includes(q));
    renderVideosTableList(filtered);
}

function renderVideosTableList(videos) {
    const tbody = document.getElementById('videos-table-body');
    if (videos.length === 0) {
        tbody.innerHTML = `<tr><td colspan="10" class="py-6 text-center text-slate-500">No videos match active filters.</td></tr>`;
        return;
    }

    tbody.innerHTML = videos.map(v => {
        const tierBadge = v.performance_tier === 'Viral Breakout'
            ? '<span class="cyber-badge cyber-badge-blue text-[10px]">Viral Outperformer</span>'
            : (v.performance_tier === 'Above Average'
                ? '<span class="cyber-badge cyber-badge-emerald text-[10px]">Above Average</span>'
                : (v.performance_tier === 'Underperforming'
                    ? '<span class="cyber-badge cyber-badge-rose text-[10px]">Underperforming</span>'
                    : '<span class="cyber-badge cyber-badge-amber text-[10px]">Baseline</span>'));

        const hookDropColor = v.intro_dropoff_30s > 30 ? 'text-rose-400 font-bold' : 'text-slate-300';
        const zColor = v.virality_robust_z >= 1.5 ? 'text-cyan-400 font-bold' : (v.virality_robust_z <= -0.5 ? 'text-rose-400' : 'text-slate-300');

        return `
            <tr class="hover:bg-slate-800/40 transition">
                <td class="py-3 px-4 font-medium text-slate-100 max-w-xs truncate" title="${v.title}">
                    <div class="truncate">${v.title}</div>
                    <div class="text-[10px] text-slate-500 mt-0.5">${Math.round(v.duration_sec / 60)}m ${v.duration_sec % 60}s · ${v.format_type}</div>
                </td>
                <td class="py-3 px-3 text-slate-400">${v.format_type}</td>
                <td class="py-3 px-3 font-mono font-semibold">${v.total_views.toLocaleString()}</td>
                <td class="py-3 px-3 font-mono">${v.total_watch_time_hrs.toLocaleString()}h</td>
                <td class="py-3 px-3 font-mono">${v.avg_view_percentage}%</td>
                <td class="py-3 px-3 font-mono ${hookDropColor}">-${v.intro_dropoff_30s}%</td>
                <td class="py-3 px-3 font-mono ${zColor}">${v.virality_robust_z > 0 ? '+' : ''}${v.virality_robust_z}</td>
                <td class="py-3 px-3 font-mono text-purple-300">+${v.sub_conversion_per_1k}</td>
                <td class="py-3 px-3">${tierBadge}</td>
                <td class="py-3 px-3 text-right">
                    <button onclick="openVideoDrilldown('${v.video_id}')" class="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-cyan-600/30 text-cyan-400 text-[11px] font-semibold border border-cyan-500/20 transition">
                        Inspect
                    </button>
                </td>
            </tr>
        `;
    }).join('');
    lucide.createIcons();
}

// =========================================================================
// TAB 3: AUDIENCE RETENTION RADAR & TIMELINE SCRUB
// =========================================================================
async function loadRetentionTab() {
    try {
        const res = await fetch('/api/v1/videos');
        currentVideosData = await res.json();
        
        const selector = document.getElementById('retention-video-selector');
        selector.innerHTML = currentVideosData.map(v => 
            `<option value="${v.video_id}">${v.title.substring(0, 48)}...</option>`
        ).join('');

        if (currentVideosData.length > 0) {
            loadRetentionDetail(currentVideosData[0].video_id);
        }
    } catch (err) {
        console.error('Failed to load retention tab:', err);
    }
}

async function loadRetentionDetail(videoId) {
    try {
        selectedRetentionVideoId = videoId;
        const res = await fetch(`/api/v1/retention/${videoId}`);
        const data = await res.json();

        document.getElementById('retention-curve-title').innerText = `Audience Retention: ${data.title}`;
        
        const r2Badge = document.getElementById('retention-r2-badge');
        if (data.is_lambda_suppressed) {
            r2Badge.className = 'cyber-badge cyber-badge-rose text-xs';
            r2Badge.innerText = `R² = ${data.retention_r2} (λ Suppressed)`;
            document.getElementById('retention-fit-explanation').innerText = 'Irregular curve pattern detected (scrubbing/rewatches). Mathematical decay parameter suppressed per Policy Rule.';
        } else {
            r2Badge.className = 'cyber-badge cyber-badge-emerald text-xs';
            r2Badge.innerText = `R² = ${data.retention_r2} (λ = ${data.retention_decay_lambda})`;
            document.getElementById('retention-fit-explanation').innerText = 'Valid non-linear least squares fit: R(t) = R₀·e⁻ᵝᵗ + C';
        }

        // Render Diagnostics Cards
        const cardsGrid = document.getElementById('retention-diagnostic-cards');
        cardsGrid.innerHTML = `
            <div class="glass-card p-3.5">
                <div class="text-[11px] text-slate-400">0-30s Hook Drop</div>
                <div class="text-xl font-black ${data.intro_dropoff_30s > 30 ? 'text-rose-400' : 'text-emerald-400'} mt-1">-${data.intro_dropoff_30s}%</div>
                <div class="text-[10px] text-slate-500 mt-0.5">${data.intro_dropoff_30s > 30 ? 'Pacing issue in opening' : 'Solid hook retention'}</div>
            </div>
            <div class="glass-card p-3.5">
                <div class="text-[11px] text-slate-400">Rewatch Spikes</div>
                <div class="text-xl font-black text-cyan-400 mt-1">${data.rewatch_spikes_count} detected</div>
                <div class="text-[10px] text-slate-500 mt-0.5">High-intent visual rewind points</div>
            </div>
            <div class="glass-card p-3.5">
                <div class="text-[11px] text-slate-400">Mid-Video Churn Dips</div>
                <div class="text-xl font-black ${data.mid_video_dips_count > 1 ? 'text-rose-400' : 'text-emerald-400'} mt-1">${data.mid_video_dips_count} detected</div>
                <div class="text-[10px] text-slate-500 mt-0.5">Sudden pacing deceleration</div>
            </div>
            <div class="glass-card p-3.5">
                <div class="text-[11px] text-slate-400">Model Goodness of Fit</div>
                <div class="text-xl font-black text-purple-400 mt-1">R² ${data.retention_r2}</div>
                <div class="text-[10px] text-slate-500 mt-0.5">Threshold: R² ≥ 0.70</div>
            </div>
        `;

        renderRetentionCurveChart(data);
        lucide.createIcons();

    } catch (err) {
        console.error('Failed to load retention detail:', err);
    }
}

function renderRetentionCurveChart(data) {
    const points = data.curve_points;
    const labels = points.map(p => `${p.second_offset}s`);
    const actuals = points.map(p => p.audience_watch_ratio);
    const fitted = points.map(p => p.fitted_ratio);

    const ctx = document.getElementById('chart-retention-curve').getContext('2d');
    if (charts.retentionCurve) charts.retentionCurve.destroy();

    charts.retentionCurve = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Observed Retention (%)',
                    data: actuals,
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.1)',
                    borderWidth: 2.5,
                    pointRadius: 0,
                    tension: 0.2,
                    fill: true
                },
                {
                    label: 'Decay Model Fit',
                    data: fitted,
                    borderColor: '#fb7185',
                    borderWidth: 1.8,
                    borderDash: [5, 4],
                    pointRadius: 0,
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    ticks: { color: '#94a3b8', maxTicksLimit: 12, font: { size: 10 } },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                },
                y: {
                    max: 100,
                    min: 0,
                    ticks: { color: '#94a3b8', font: { size: 10 } },
                    grid: { color: 'rgba(255, 255, 255, 0.05)' }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function handleTimelineScrub(e) {
    const track = document.getElementById('timeline-scrub-track');
    const needle = document.getElementById('timeline-scrub-needle');
    const label = document.getElementById('scrub-timestamp-label');
    const pill = document.getElementById('scrub-diagnostic-pill');
    if (!track || !needle || !label || !pill) return;

    const rect = track.getBoundingClientRect();
    const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    needle.style.left = `${(ratio * 100).toFixed(2)}%`;

    const totalDuration = 1080; // Default or active video duration
    const currentSec = Math.round(ratio * totalDuration);
    const mins = Math.floor(currentSec / 60);
    const secs = currentSec % 60;
    const timeStr = `${mins}:${secs < 10 ? '0' : ''}${secs}`;

    label.innerText = `Timeline Scrubber: ${timeStr} (${(ratio * 100).toFixed(1)}%)`;

    if (ratio <= 0.15) {
        pill.innerText = `Opening Hook Zone: 0-30s drop-off critical for algorithmic shelf-life`;
        pill.className = 'text-rose-400 font-bold';
    } else if (ratio >= 0.88) {
        pill.innerText = `Outro CTA Phase: Keep end-screens under 15 seconds to maximize conversion`;
        pill.className = 'text-emerald-400 font-bold';
    } else {
        pill.innerText = `Content Pacing Body: Smooth exponential decay with key diagram spikes`;
        pill.className = 'text-cyan-400 font-medium';
    }
}

function resetTimelineScrub() {
    const label = document.getElementById('scrub-timestamp-label');
    const pill = document.getElementById('scrub-diagnostic-pill');
    if (label) label.innerText = 'Hover along timeline to inspect moments';
    if (pill) {
        pill.innerText = 'Scrub needle over video timeline to view instantaneous drop-offs';
        pill.className = 'text-slate-300 font-medium';
    }
}

// =========================================================================
// TAB 4: TRAFFIC EFFICIENCY QUADRANTS
// =========================================================================
async function loadTrafficTab() {
    try {
        const res = await fetch('/api/v1/traffic-sources');
        const items = await res.json();

        // Bar Chart
        const labels = items.map(i => i.traffic_source_type);
        const viewShares = items.map(i => i.view_share_pct);
        const watchShares = items.map(i => i.watch_share_pct);

        const ctxBars = document.getElementById('chart-traffic-bars').getContext('2d');
        if (charts.trafficBars) charts.trafficBars.destroy();
        charts.trafficBars = new Chart(ctxBars, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    { label: 'View Share %', data: viewShares, backgroundColor: 'rgba(56, 189, 248, 0.8)', borderRadius: 6 },
                    { label: 'Watch Share %', data: watchShares, backgroundColor: 'rgba(16, 185, 129, 0.8)', borderRadius: 6 }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                    y: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
                }
            }
        });

        // Doughnut Chart
        const ctxDoughnut = document.getElementById('chart-traffic-doughnut').getContext('2d');
        if (charts.trafficDoughnut) charts.trafficDoughnut.destroy();
        charts.trafficDoughnut = new Chart(ctxDoughnut, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: viewShares,
                    backgroundColor: ['#38bdf8', '#34d399', '#818cf8', '#fbbf24', '#fb7185'],
                    borderColor: '#0f172a',
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { color: '#cbd5e1', font: { size: 10 } } } }
            }
        });

        // Quadrant Cards
        const grid = document.getElementById('traffic-quadrant-cards');
        grid.innerHTML = items.map(i => `
            <div class="glass-card p-4">
                <div class="flex items-center justify-between">
                    <span class="font-bold text-xs text-white">${i.traffic_source_type}</span>
                    <span class="cyber-badge cyber-badge-blue text-[9px]">${i.quadrant}</span>
                </div>
                <div class="mt-3 flex items-baseline justify-between text-xs">
                    <span class="text-slate-400">View Share:</span>
                    <span class="font-mono font-bold text-white">${i.view_share_pct}%</span>
                </div>
                <div class="mt-1 flex items-baseline justify-between text-xs">
                    <span class="text-slate-400">Watch Share:</span>
                    <span class="font-mono font-bold text-emerald-400">${i.watch_share_pct}%</span>
                </div>
                <div class="mt-1 flex items-baseline justify-between text-xs">
                    <span class="text-slate-400">Efficiency Ratio:</span>
                    <span class="font-mono font-bold ${i.efficiency_ratio >= 1.0 ? 'text-cyan-400' : 'text-rose-400'}">${i.efficiency_ratio}x</span>
                </div>
            </div>
        `).join('');

    } catch (err) {
        console.error('Failed to load traffic tab:', err);
    }
}

// =========================================================================
// TAB 5: DEMOGRAPHICS
// =========================================================================
async function loadAudienceTab() {
    try {
        const res = await fetch('/api/v1/demographics');
        const rows = await res.json();

        const ageRows = rows.filter(r => r.dimension_type === 'ageGroup');
        const geoRows = rows.filter(r => r.dimension_type === 'country');

        // Age Chart
        const ctxAge = document.getElementById('chart-demographics-age').getContext('2d');
        if (charts.demoAge) charts.demoAge.destroy();
        charts.demoAge = new Chart(ctxAge, {
            type: 'bar',
            data: {
                labels: ageRows.map(r => r.dimension_value),
                datasets: [{
                    label: 'Audience %',
                    data: ageRows.map(r => r.viewer_percentage),
                    backgroundColor: 'rgba(56, 189, 248, 0.8)',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                    y: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
                },
                plugins: { legend: { display: false } }
            }
        });

        // Geo Chart
        const ctxGeo = document.getElementById('chart-demographics-geo').getContext('2d');
        if (charts.demoGeo) charts.demoGeo.destroy();
        charts.demoGeo = new Chart(ctxGeo, {
            type: 'bar',
            data: {
                labels: geoRows.map(r => r.dimension_value),
                datasets: [{
                    label: 'Audience %',
                    data: geoRows.map(r => r.viewer_percentage),
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                    y: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
                },
                plugins: { legend: { display: false } }
            }
        });
    } catch (err) {
        console.error('Failed to load audience tab:', err);
    }
}

// =========================================================================
// TAB 6: CONTENT INTELLIGENCE
// =========================================================================
async function loadContentIntelligenceTab() {
    try {
        const res = await fetch('/api/v1/content-intelligence');
        const clusters = await res.json();

        const grid = document.getElementById('content-clusters-grid');
        grid.innerHTML = clusters.map(c => `
            <div class="glass-card p-5 space-y-3">
                <div class="flex items-center justify-between">
                    <div>
                        <h3 class="font-bold text-sm text-white">${c.cluster_name}</h3>
                        <p class="text-xs text-slate-400">${c.sample_titles ? c.sample_titles.length : 0} videos in pillar</p>
                    </div>
                    <span class="cyber-badge cyber-badge-blue text-[10px]">${c.opportunity_score}/100 Opp Score</span>
                </div>
                <div class="grid grid-cols-2 gap-3 text-xs">
                    <div class="p-2.5 bg-slate-900/60 rounded-xl">
                        <div class="text-[10px] text-slate-400">Total Views</div>
                        <div class="text-sm font-bold text-white mt-0.5">${c.total_views.toLocaleString()}</div>
                    </div>
                    <div class="p-2.5 bg-slate-900/60 rounded-xl">
                        <div class="text-[10px] text-slate-400">Avg Retention</div>
                        <div class="text-sm font-bold text-emerald-400 mt-0.5">${c.avg_view_percentage}%</div>
                    </div>
                </div>
                <div>
                    <div class="text-[10px] uppercase font-bold text-slate-500 mb-1">Keywords:</div>
                    <div class="flex flex-wrap gap-1.5">
                        ${(c.top_keywords || []).map(k => `<span class="px-2 py-0.5 rounded bg-slate-800 text-[10px] text-slate-300 font-mono">${k}</span>`).join('')}
                    </div>
                </div>
            </div>
        `).join('');

    } catch (err) {
        console.error('Failed to load content intelligence:', err);
    }
}

// =========================================================================
// TAB 7: PRE-PUBLISH NEURAL SIMULATOR
// =========================================================================
function initTitleAnalyzer() {
    analyzeDraftTitleLive();
}

function analyzeDraftTitleLive() {
    const input = document.getElementById('sim-title');
    const charCount = document.getElementById('title-char-count');
    const scoreVal = document.getElementById('title-power-score');
    const meterFill = document.getElementById('title-meter-fill');
    const mobilePreview = document.getElementById('mobile-preview-title');
    const mobileTruncStatus = document.getElementById('mobile-trunc-status');
    if (!input || !charCount || !scoreVal || !meterFill) return;

    const title = input.value.trim();
    const len = title.length;
    charCount.innerText = `${len} chars`;

    if (mobilePreview) mobilePreview.innerText = title || 'Draft Video Title';

    // Scoring heuristics
    let score = 50;
    if (len >= 45 && len <= 65) score += 25;
    else if (len > 70) score -= 20;

    const hasNumber = /\d+/.test(title);
    if (hasNumber) score += 10;

    const powerWords = ['architecture', 'production', 'deep dive', 'scale', 'masterclass', 'why', 'how', 'distributed'];
    const matchedWords = powerWords.filter(w => title.toLowerCase().includes(w));
    score += Math.min(15, matchedWords.length * 5);

    score = Math.max(10, Math.min(100, score));

    scoreVal.innerText = `${score} / 100 (${score >= 80 ? 'Optimal' : (score >= 60 ? 'Good' : 'Needs Optimization')})`;
    meterFill.style.width = `${score}%`;

    if (score >= 80) {
        meterFill.className = 'title-meter-fill bg-gradient-to-r from-emerald-500 to-cyan-400';
    } else if (score >= 60) {
        meterFill.className = 'title-meter-fill bg-gradient-to-r from-blue-500 to-amber-400';
    } else {
        meterFill.className = 'title-meter-fill bg-gradient-to-r from-amber-500 to-rose-500';
    }

    if (mobileTruncStatus) {
        if (len > 70) {
            mobileTruncStatus.innerText = '⚠ Likely truncated on mobile feed';
            mobileTruncStatus.className = 'text-[10px] text-rose-400 font-bold';
        } else {
            mobileTruncStatus.innerText = '✓ Fits within 3 lines on mobile';
            mobileTruncStatus.className = 'text-[10px] text-emerald-400';
        }
    }
}

function applyTitleArchetype(archetype) {
    const input = document.getElementById('sim-title');
    if (!input) return;

    if (archetype === 'curiosity') {
        input.value = 'The Hidden Distributed Architecture Pattern Nobody Talks About';
    } else if (archetype === 'numbers') {
        input.value = 'How We Scaled Our Distributed SQLite Cluster to 10M Requests/Day';
    } else if (archetype === 'contrarian') {
        input.value = 'Why Senior Engineers Are Abandoning Traditional Microservices in 2026';
    } else if (archetype === 'masterclass') {
        input.value = 'Distributed Systems & Raft Consensus: The Complete Masterclass';
    }

    analyzeDraftTitleLive();
    showToast(`Applied ${archetype} hook template`, 'success');
    runSimulation();
}

function updateSimDuration(sec) {
    const durationSpan = document.getElementById('sim-duration-val');
    const mins = Math.floor(sec / 60);
    const s = sec % 60;
    if (durationSpan) {
        durationSpan.innerText = `${mins}m ${s > 0 ? s + 's' : ''} (${sec}s)`;
    }
}

async function runSimulation() {
    try {
        const title = document.getElementById('sim-title').value;
        const durationSec = parseInt(document.getElementById('sim-duration').value);
        const day = parseInt(document.getElementById('sim-day').value);
        const hour = parseInt(document.getElementById('sim-hour').value);

        const res = await fetch('/api/v1/predictions/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title: title,
                duration_sec: durationSec,
                publish_day: day,
                publish_hour: hour
            })
        });
        const data = await res.json();

        document.getElementById('sim-pred-views').innerText = data.predicted_views.toLocaleString();
        document.getElementById('sim-ci-range').innerText = `80% CI: ${(data.ci_lower / 1000).toFixed(1)}k - ${(data.ci_upper / 1000).toFixed(1)}k`;
        document.getElementById('sim-pred-watch').innerText = `${data.predicted_watch_hours.toLocaleString()} hrs`;
        document.getElementById('sim-pred-ret').innerText = `${data.predicted_retention_pct}%`;

        const badge = document.getElementById('sim-tier-badge');
        badge.innerText = data.tier;
        badge.className = data.tier === 'Viral Breakout Potential' ? 'cyber-badge cyber-badge-blue text-xs' : 'cyber-badge cyber-badge-emerald text-xs';

        const list = document.getElementById('sim-improvements-list');
        list.innerHTML = (data.improvements || []).map(imp => `
            <li class="flex items-start space-x-2 text-slate-300">
                <i data-lucide="arrow-right" class="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5"></i>
                <span>${imp}</span>
            </li>
        `).join('');

        lucide.createIcons();
    } catch (err) {
        console.error('Failed to run simulation:', err);
    }
}

// =========================================================================
// TAB 8: 90-DAY COMPOUNDING SCENARIO PLANNER
// =========================================================================
function initCompoundingScenarioPlanner() {
    updateScenarioPlanner();
}

function updateScenarioPlanner() {
    const cadence = parseInt(document.getElementById('lever-cadence')?.value || 2);
    const hook = parseInt(document.getElementById('lever-hook')?.value || 10);
    const deepdive = parseInt(document.getElementById('lever-deepdive')?.value || 60);

    document.getElementById('lever-cadence-val').innerText = `${cadence} uploads / week`;
    document.getElementById('lever-hook-val').innerText = `+${hook}% lift`;
    document.getElementById('lever-deepdive-val').innerText = `${deepdive}% of uploads`;

    // Mathematical Compounding Simulation:
    // Base uploads = cadence * 12.8 weeks
    const totalUploads = cadence * 13;
    const avgViewsPerUpload = 32000 * (1 + (hook * 0.025)) * (1 + (deepdive * 0.003));
    const viewsLift = Math.round(totalUploads * avgViewsPerUpload);
    const subsLift = Math.round((viewsLift / 1000) * 6.8);
    const watchHoursLift = Math.round((viewsLift * (deepdive > 50 ? 12 : 6)) / 60);

    document.getElementById('scenario-views-lift').innerText = `+${viewsLift.toLocaleString()}`;
    document.getElementById('scenario-subs-lift').innerText = `+${subsLift.toLocaleString()}`;
    document.getElementById('scenario-watch-lift').innerText = `+${watchHoursLift.toLocaleString()} hrs`;

    // Plot compounding trajectory
    const weeks = [1, 2, 4, 6, 8, 10, 12];
    const trajectoryData = weeks.map(w => Math.round((w / 12) * (viewsLift * (1 + (w * 0.04)))));

    const ctx = document.getElementById('chart-scenario-projection')?.getContext('2d');
    if (ctx) {
        if (charts.scenarioProj) charts.scenarioProj.destroy();
        charts.scenarioProj = new Chart(ctx, {
            type: 'line',
            data: {
                labels: weeks.map(w => `Week ${w}`),
                datasets: [{
                    label: 'Projected Cumulative Views',
                    data: trajectoryData,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2.5,
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                    y: { ticks: { color: '#34d399', font: { size: 10 } }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
                },
                plugins: { legend: { display: false } }
            }
        });
    }
}

// =========================================================================
// TAB 9: GROWTH OPPORTUNITY MATRIX
// =========================================================================
async function loadGrowthMatrix() {
    try {
        const res = await fetch(`/api/v1/growth-matrix?is_brutal=${isBrutalMode}`);
        const matrix = await res.json();

        const renderQuadrant = (containerId, items) => {
            const el = document.getElementById(containerId);
            if (!el) return;
            if (!items || items.length === 0) {
                el.innerHTML = '<div class="text-xs text-slate-500 italic">No recommendations in this quadrant.</div>';
                return;
            }
            el.innerHTML = items.map(item => `
                <div class="p-3 bg-slate-900/60 rounded-xl border border-darkborder space-y-1.5 hover:border-slate-600 transition">
                    <div class="flex items-center justify-between">
                        <span class="font-bold text-xs text-slate-200">${item.title}</span>
                        <span class="cyber-badge cyber-badge-blue text-[9px]">P ${item.priority_score}</span>
                    </div>
                    <p class="text-[11px] text-slate-400">${item.recommendation_text}</p>
                    <button onclick="openEvidenceModal('${item.rec_id}')" class="text-[10px] text-cyan-400 hover:underline flex items-center gap-1 font-semibold pt-1">
                        <i data-lucide="file-check-2" class="w-3 h-3"></i>
                        <span>Inspect Grounding Evidence</span>
                    </button>
                </div>
            `).join('');
            items.forEach(i => { allEvidenceStore[i.rec_id] = i.evidence_object; });
        };

        renderQuadrant('matrix-quick-wins', matrix.quick_wins);
        renderQuadrant('matrix-strategic', matrix.strategic_flagships);
        renderQuadrant('matrix-fillins', matrix.fill_ins);
        renderQuadrant('matrix-deprioritize', matrix.deprioritize);

        lucide.createIcons();
    } catch (err) {
        console.error('Failed to load growth matrix:', err);
    }
}

// =========================================================================
// TAB 10: STRATEGIC RECOMMENDATIONS & EVIDENCE OBJECTS
// =========================================================================
let currentRecsCache = [];

async function loadRecommendations() {
    try {
        const res = await fetch(`/api/v1/recommendations?is_brutal=${isBrutalMode}`);
        const recs = await res.json();
        currentRecsCache = recs;
        renderRecsList(recs);
    } catch (err) {
        console.error('Failed to load recommendations:', err);
    }
}

function filterRecsCategory(cat) {
    document.querySelectorAll('[id^="rec-filter-"]').forEach(btn => {
        btn.className = 'px-3 py-1 rounded-lg bg-slate-800 text-slate-400 hover:text-white transition';
    });
    const activeBtn = document.getElementById(`rec-filter-${cat}`);
    if (activeBtn) {
        activeBtn.className = 'px-3 py-1 rounded-lg bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-semibold';
    }

    if (cat === 'ALL') {
        renderRecsList(currentRecsCache);
    } else {
        const filtered = currentRecsCache.filter(r => r.category === cat);
        renderRecsList(filtered);
    }
}

function renderRecsList(recs) {
    const container = document.getElementById('recommendations-container');
    if (!container) return;

    if (recs.length === 0) {
        container.innerHTML = `<div class="p-6 text-center text-slate-500 text-xs">No recommendations found for active category.</div>`;
        return;
    }

    container.innerHTML = recs.map(r => {
        allEvidenceStore[r.rec_id] = r.evidence_object;

        const borderClass = r.is_brutal ? 'border-rose-500/40 hover:border-rose-500/60' : 'border-white/10 hover:border-cyan-500/40';
        const badge = r.is_brutal 
            ? '<span class="cyber-badge cyber-badge-rose text-[10px]">Brutal Diagnostic Audit</span>' 
            : '<span class="cyber-badge cyber-badge-emerald text-[10px]">Strategic Leverage</span>';

        return `
            <div class="glass-card p-5 space-y-3 ${borderClass}">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-darkborder pb-3">
                    <div class="flex items-center space-x-2.5">
                        ${badge}
                        <span class="text-xs font-semibold text-slate-400">${r.category}</span>
                    </div>
                    <div class="flex items-center space-x-2 text-xs">
                        <span class="text-slate-400">Priority Score:</span>
                        <span class="font-mono font-black text-cyan-400">${r.priority_score}</span>
                        <span class="text-slate-500">|</span>
                        <span class="text-slate-400">Impact:</span>
                        <span class="font-bold text-white">${r.impact_score}</span>
                    </div>
                </div>

                <h3 class="font-bold text-base text-slate-100">${r.title}</h3>
                <p class="text-xs text-slate-300 leading-relaxed">${r.recommendation_text}</p>

                <div class="flex flex-wrap items-center justify-between pt-2 text-xs gap-3">
                    <button onclick="openEvidenceModal('${r.rec_id}')" class="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-cyan-400 font-semibold border border-cyan-500/30 flex items-center space-x-1.5 transition">
                        <i data-lucide="shield-check" class="w-3.5 h-3.5"></i>
                        <span>Inspect Grounding Evidence</span>
                    </button>

                    <button onclick="switchTab('predictions')" class="text-slate-400 hover:text-white flex items-center gap-1 font-semibold">
                        <span>Test in Simulator</span>
                        <i data-lucide="arrow-right" class="w-3.5 h-3.5"></i>
                    </button>
                </div>
            </div>
        `;
    }).join('');

    lucide.createIcons();
}

function openEvidenceModal(recId) {
    const ev = allEvidenceStore[recId];
    if (!ev) return;

    const modal = document.getElementById('evidence-modal');
    const body = document.getElementById('evidence-content-body');
    if (!modal || !body) return;

    body.innerHTML = `
        <div class="p-3 bg-slate-900/80 rounded-xl space-y-2 border border-darkborder">
            <div class="flex justify-between">
                <span class="text-slate-400">Metric Analyzed:</span>
                <span class="font-bold text-white text-right">${ev.metric}</span>
            </div>
            <div class="flex justify-between">
                <span class="text-slate-400">Observed Value:</span>
                <span class="font-mono font-bold text-cyan-400">${ev.observed_value}</span>
            </div>
            <div class="flex justify-between">
                <span class="text-slate-400">Channel Baseline:</span>
                <span class="font-mono font-bold text-slate-300">${ev.baseline}</span>
            </div>
            <div class="flex justify-between">
                <span class="text-slate-400">Effect Size:</span>
                <span class="font-mono font-bold text-emerald-400">${ev.effect_size > 0 ? '+' : ''}${ev.effect_size}%</span>
            </div>
            <div class="flex justify-between">
                <span class="text-slate-400">Sample Size (n):</span>
                <span class="font-mono text-white">${ev.n} uploads</span>
            </div>
            <div class="flex justify-between">
                <span class="text-slate-400">Confidence Level:</span>
                <span class="font-mono text-purple-400 font-bold">${Math.round(ev.confidence * 100)}%</span>
            </div>
        </div>

        <div class="space-y-1">
            <span class="text-slate-400 font-semibold text-[11px] uppercase tracking-wider">Limitations & Edge Cases:</span>
            <p class="text-slate-300 text-xs italic">${ev.limitations}</p>
        </div>

        <div class="text-[10px] text-slate-500 font-mono">
            <strong>Provenance:</strong> ${ev.provenance_sources}
        </div>
    `;

    modal.classList.remove('hidden');
    lucide.createIcons();
}

function closeEvidenceModal() {
    const modal = document.getElementById('evidence-modal');
    if (modal) modal.classList.add('hidden');
}

// =========================================================================
// VIDEO DRILLDOWN MODAL
// =========================================================================
async function openVideoDrilldown(videoId) {
    try {
        const modal = document.getElementById('video-drilldown-modal');
        if (!modal) return;

        const v = currentVideosData.find(x => x.video_id === videoId) || currentVideosData[0];
        document.getElementById('drill-video-title').innerText = v.title;
        document.getElementById('drill-format-badge').innerText = v.format_type;
        document.getElementById('drill-duration-text').innerText = `Duration: ${Math.round(v.duration_sec / 60)}m ${v.duration_sec % 60}s`;

        document.getElementById('drill-metrics-grid').innerHTML = `
            <div class="p-2.5 bg-slate-900/60 rounded-xl">
                <div class="text-slate-400 text-[10px]">Views</div>
                <div class="text-sm font-bold text-white mt-0.5">${v.total_views.toLocaleString()}</div>
            </div>
            <div class="p-2.5 bg-slate-900/60 rounded-xl">
                <div class="text-slate-400 text-[10px]">Watch Hours</div>
                <div class="text-sm font-bold text-cyan-400 mt-0.5">${v.total_watch_time_hrs.toLocaleString()}h</div>
            </div>
            <div class="p-2.5 bg-slate-900/60 rounded-xl">
                <div class="text-slate-400 text-[10px]">Avg Retention</div>
                <div class="text-sm font-bold text-emerald-400 mt-0.5">${v.avg_view_percentage}%</div>
            </div>
            <div class="p-2.5 bg-slate-900/60 rounded-xl">
                <div class="text-slate-400 text-[10px]">Virality Z</div>
                <div class="text-sm font-bold text-purple-400 mt-0.5">${v.virality_robust_z}</div>
            </div>
        `;

        // Fetch Retention Curve for drilldown
        const rRes = await fetch(`/api/v1/retention/${videoId}`);
        const rData = await rRes.json();

        const ctx = document.getElementById('chart-drilldown-retention').getContext('2d');
        if (charts.drilldownRetention) charts.drilldownRetention.destroy();
        charts.drilldownRetention = new Chart(ctx, {
            type: 'line',
            data: {
                labels: rData.curve_points.map(p => `${p.second_offset}s`),
                datasets: [{
                    label: 'Retention %',
                    data: rData.curve_points.map(p => p.audience_watch_ratio),
                    borderColor: '#38bdf8',
                    backgroundColor: 'rgba(56, 189, 248, 0.15)',
                    fill: true,
                    tension: 0.2,
                    pointRadius: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { ticks: { color: '#94a3b8', font: { size: 9 }, maxTicksLimit: 10 }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                    y: { max: 100, min: 0, ticks: { color: '#94a3b8', font: { size: 9 } }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
                },
                plugins: { legend: { display: false } }
            }
        });

        // Diagnostic points
        document.getElementById('drill-recommendations-list').innerHTML = `
            <div class="p-3 bg-slate-900/60 rounded-xl border border-darkborder text-xs text-slate-300">
                0-30s Hook Drop-Off is <strong>${rData.intro_dropoff_30s}%</strong>. 
                ${rData.intro_dropoff_30s > 30 ? 'Pacing issue: The opening failed to validate thumbnail premises immediately.' : 'Strong opening retention.'}
            </div>
            <div class="p-3 bg-slate-900/60 rounded-xl border border-darkborder text-xs text-slate-300">
                Detected <strong>${rData.rewatch_spikes_count} re-watch spikes</strong>: Viewers actively rewound to re-inspect code explanations.
            </div>
        `;

        modal.classList.remove('hidden');
        lucide.createIcons();
    } catch (err) {
        console.error('Failed to open video drilldown:', err);
    }
}

function closeDrilldownModal() {
    const modal = document.getElementById('video-drilldown-modal');
    if (modal) modal.classList.add('hidden');
}

// =========================================================================
// TAB 11: EXECUTIVE REPORTS & EXPORTS
// =========================================================================
function updateReportsView() {
    const reportTitle = document.getElementById('report-preview-title');
    if (reportTitle) {
        reportTitle.innerText = isBrutalMode 
            ? 'Executive Channel Growth Report (BRUTAL STRATEGIC AUDIT MODE)' 
            : 'Executive Channel Growth Report (Standard Mode)';
    }
}

function downloadReport(type) {
    if (type === 'pdf') {
        const mode = isBrutalMode ? 'brutal' : 'standard';
        showToast('Compiling executive PDF report...', 'info');
        window.open(`/api/v1/reports/pdf?report_type=${mode}`, '_blank');
    } else if (type === 'csv') {
        showToast('Exporting warehouse dataset to CSV...', 'info');
        window.open('/api/v1/reports/export/csv', '_blank');
    }
}

function openHtmlReport() {
    const mode = isBrutalMode ? 'brutal' : 'standard';
    window.open(`/api/v1/reports/view?report_type=${mode}`, '_blank');
}

// =========================================================================
// TAB 12: DATA SOURCES & 30-DAY COMPLIANCE
// =========================================================================
async function loadComplianceHeader() {
    try {
        const res = await fetch('/api/v1/compliance/status');
        const data = await res.json();
        const ttlSpan = document.getElementById('top-ttl-days');
        if (ttlSpan && data.days_to_earliest_ttl !== undefined) {
            ttlSpan.innerText = `${data.days_to_earliest_ttl}d remaining`;
        }
    } catch (err) {
        console.error('Failed to load compliance header:', err);
    }
}

async function loadComplianceTab() {
    try {
        const cRes = await fetch('/api/v1/compliance/status');
        const comp = await cRes.json();

        const qRes = await fetch('/api/v1/quota/status');
        const quota = await qRes.json();

        const grid = document.getElementById('compliance-stats-grid');
        grid.innerHTML = `
            <div class="glass-card p-4">
                <div class="text-[11px] text-slate-400">Raw Telemetry Records</div>
                <div class="text-2xl font-black text-white mt-1">${comp.raw_video_count + comp.raw_daily_rows + comp.raw_retention_points}</div>
                <div class="text-[10px] text-slate-500 mt-0.5">Subject to 30d TTL purge</div>
            </div>
            <div class="glass-card p-4">
                <div class="text-[11px] text-slate-400">Derived Permanent Metrics</div>
                <div class="text-2xl font-black text-cyan-400 mt-1">${comp.derived_metrics_count}</div>
                <div class="text-[10px] text-emerald-400 mt-0.5">Compliant permanent storage</div>
            </div>
            <div class="glass-card p-4">
                <div class="text-[11px] text-slate-400">Daily API Quota Remaining</div>
                <div class="text-2xl font-black text-white mt-1">${(quota.daily_quota_limit - quota.quota_units_used_today).toLocaleString()}</div>
                <div class="text-[10px] text-slate-400 mt-0.5">Used: ${quota.quota_units_used_today} / ${quota.daily_quota_limit}</div>
            </div>
            <div class="glass-card p-4">
                <div class="text-[11px] text-slate-400">Earliest Expiration Date</div>
                <div class="text-2xl font-black text-emerald-400 mt-1">${comp.days_to_earliest_ttl} days</div>
                <div class="text-[10px] text-slate-500 mt-0.5">Policy Section III.E.4 verified</div>
            </div>
        `;

        loadComplianceLogs();
    } catch (err) {
        console.error('Failed to load compliance tab:', err);
    }
}

async function loadComplianceLogs() {
    try {
        const res = await fetch('/api/v1/compliance/logs');
        const logs = await res.json();
        const tbody = document.getElementById('compliance-logs-body');
        if (!tbody) return;

        if (logs.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="py-4 text-center text-slate-500 text-xs">No purge sweeps logged yet. System in compliant grace window.</td></tr>`;
            return;
        }

        tbody.innerHTML = logs.map(l => `
            <tr>
                <td class="py-2.5 px-4 font-mono text-[11px]">${l.timestamp ? l.timestamp.substring(0, 16) : 'N/A'}</td>
                <td class="py-2.5 px-3"><span class="cyber-badge cyber-badge-blue text-[10px]">${l.event_type}</span></td>
                <td class="py-2.5 px-3 text-slate-300">${l.table_name}</td>
                <td class="py-2.5 px-3 font-mono">${l.records_affected}</td>
                <td class="py-2.5 px-3 text-emerald-400 font-bold">${l.action_taken}</td>
            </tr>
        `).join('');

    } catch (err) {
        console.error('Failed to load compliance logs:', err);
    }
}

async function triggerTtlSweep() {
    try {
        showToast('Executing 30-Day TTL Purge Sweeper...', 'info');
        const res = await fetch('/api/v1/compliance/sweep', { method: 'POST' });
        const result = await res.json();
        showToast(`Sweep verified: ${result.total_purged} expired raw records purged`, 'success');
        loadComplianceTab();
    } catch (err) {
        console.error('Failed to trigger sweep:', err);
        showToast('Sweep error occurred', 'warning');
    }
}

// =========================================================================
// TAB 13: ML MODEL CENTER
// =========================================================================
async function loadModelCenter() {
    try {
        const res = await fetch('/api/v1/model-center');
        const data = await res.json();

        // Feature Importances Bar Chart
        const featEntries = Object.entries(data.feature_importances || {}).slice(0, 8);
        const ctx = document.getElementById('chart-model-features').getContext('2d');
        if (charts.modelFeatures) charts.modelFeatures.destroy();
        charts.modelFeatures = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: featEntries.map(e => e[0]),
                datasets: [{
                    label: 'Feature Importance Weight',
                    data: featEntries.map(e => e[1]),
                    backgroundColor: 'rgba(56, 189, 248, 0.85)',
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                    y: { ticks: { color: '#cbd5e1', font: { size: 10 } }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
                },
                plugins: { legend: { display: false } }
            }
        });

        // Benchmark Scorecard
        const list = document.getElementById('model-scorecard-list');
        list.innerHTML = `
            <div class="p-3 bg-slate-900/60 rounded-xl space-y-1">
                <div class="text-slate-400 text-[11px]">Champion Model</div>
                <div class="text-sm font-bold text-white">${data.champion_model}</div>
            </div>
            <div class="p-3 bg-slate-900/60 rounded-xl space-y-1">
                <div class="text-slate-400 text-[11px]">Model MAE Error</div>
                <div class="text-sm font-bold text-emerald-400">${data.champion_mae} views</div>
                <div class="text-[10px] text-slate-500">Naive Median Baseline: ${data.naive_baseline_mae} views</div>
            </div>
            <div class="p-3 bg-slate-900/60 rounded-xl space-y-1">
                <div class="text-slate-400 text-[11px]">MAE Uplift vs Baseline</div>
                <div class="text-xl font-black text-cyan-400">+${data.mae_improvement_pct}%</div>
                <div class="text-[10px] text-emerald-400 font-semibold">Statistically verified predictive lift</div>
            </div>
            <div class="p-3 bg-slate-900/60 rounded-xl space-y-1">
                <div class="text-slate-400 text-[11px]">Temporal Cutoff Rule</div>
                <div class="text-xs text-slate-300">Strictly zero post-publish metrics used (No likes, views, or comments from t > 0).</div>
            </div>
        `;
    } catch (err) {
        console.error('Failed to load model center:', err);
    }
}

// Resync Data Trigger
async function triggerReseed() {
    try {
        showToast('Resynchronizing warehouse telemetry...', 'info');
        const res = await fetch('/api/v1/sync/seed', { method: 'POST' });
        const result = await res.json();
        showToast('Warehouse telemetry resynced successfully!', 'success');
        await loadDashboard();
        await loadComplianceHeader();
    } catch (err) {
        console.error('Failed to reseed:', err);
        showToast('Failed to resync data', 'warning');
    }
}

// Enterprise Ecosystem Benchmarks Loader
async function loadBenchmarkTab() {
    try {
        const res = await fetch('/api/v1/enterprise-benchmarks');
        if (!res.ok) {
            showToast('Failed to retrieve enterprise benchmarks', 'warning');
            return;
        }
        const data = await res.json();

        // 1. Tubular Labs V30 & ER30
        const v30El = document.getElementById('benchmark-v30-views');
        const er30El = document.getElementById('benchmark-er30-rate');
        if (v30El && data.tubular_labs_benchmark) {
            v30El.textContent = Math.round(data.tubular_labs_benchmark.channel_v30_views).toLocaleString();
            er30El.textContent = `${data.tubular_labs_benchmark.channel_er30_pct}%`;
        }

        // 2. HypeAuditor AQS
        const aqsEl = document.getElementById('benchmark-aqs-score');
        const aqsTierEl = document.getElementById('benchmark-aqs-tier');
        const aqsAuthEl = document.getElementById('benchmark-aqs-auth');
        if (aqsEl && data.hypeauditor_aqs) {
            aqsEl.textContent = data.hypeauditor_aqs.aqs_score;
            aqsTierEl.textContent = data.hypeauditor_aqs.quality_tier;
            aqsAuthEl.textContent = `${data.hypeauditor_aqs.engagement_authenticity_pct}% Human`;
        }

        // 3. NoxInfluencer Sponsorship FMV
        const cpmEl = document.getElementById('benchmark-cpm-rate');
        const fmvEl = document.getElementById('benchmark-fmv-val');
        const fmvTierEl = document.getElementById('benchmark-fmv-tier');
        if (cpmEl && data.noxinfluencer_valuation) {
            cpmEl.textContent = `$${data.noxinfluencer_valuation.effective_cpm} CPM`;
            fmvEl.textContent = `$${Number(data.noxinfluencer_valuation.estimated_60s_integration_value_usd).toLocaleString()}`;
            fmvTierEl.textContent = data.noxinfluencer_valuation.commercial_attractiveness_tier;
        }

        lucide.createIcons();
    } catch (err) {
        console.error('Failed to load enterprise benchmarks:', err);
    }
}

