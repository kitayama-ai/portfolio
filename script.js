// プロジェクトデータ（GitHubから動的に読み込むことも可能）
const projectsData = [
    {
        title: "コンビニ新着商品自動収集・LINE配信システム",
        description: "セブンイレブン、ファミリーマート、ローソンのHPを週1回自動巡回し、新着商品から高タンパク低脂質商品を自動抽出してLINE公式アカウントにカード形式で配信するシステム。",
        tech: ["Python", "スクレイピング", "LINE Messaging API", "定期実行"],
        github: "https://github.com/kitayama-ai/convenience-store-product-system",
        demo: null
    },
    {
        title: "AI広告ダッシュボード",
        description: "AIを活用した広告効果を可視化・分析するダッシュボードシステム。広告データの自動収集、分析、レポート生成を自動化。",
        tech: ["Python", "データ分析", "ダッシュボード"],
        github: "https://github.com/kitayama-ai/ai-ad-dashboard",
        demo: null
    },
    {
        title: "AIおばちゃんLP",
        description: "AIを活用したターゲット層向けランディングページ。モダンなデザインとレスポンシブ対応により、高いコンバージョン率を実現。",
        tech: ["HTML", "CSS", "JavaScript", "レスポンシブデザイン"],
        github: "https://github.com/kitayama-ai/ai-obachan-lp",
        demo: null
    },
    {
        title: "カウンセラー自動フィードバックシステム",
        description: "管理画面から相談率を監視し、基準を下回った場合にAIが過去の相談ログを分析して改善案をカウンセラー本人のLINEへ自動送付するシステム。",
        tech: ["Python", "Playwright", "n8n", "OpenAI API", "LINE Messaging API", "Google Sheets API", "Docker"],
        github: null, // GitHubリポジトリが公開され次第追加
        demo: null
    },
    {
        title: "AIエージェントシステム",
        description: "11種類のAIエージェント（コピーライター、クリエイティブディレクター、全体ディレクター、アートディレクター、薬機法監査、フィードバック担当など）が協調して広告コピーを制作するマルチエージェント協調システム。",
        tech: ["Python", "AIエージェント", "マルチエージェント協調", "11種類のエージェント"],
        github: null, // GitHubリポジトリが公開され次第追加
        demo: null
    }
];

// プロジェクトカードを生成
function createProjectCard(project) {
    const card = document.createElement('div');
    card.className = 'project-card';

    let linksHTML = '';
    if (project.github) {
        linksHTML += `
            <a href="${project.github}" target="_blank" rel="noopener noreferrer" class="project-link">
                <svg class="icon" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                GitHub
            </a>
        `;
    }
    if (project.demo) {
        linksHTML += `
            <a href="${project.demo}" target="_blank" rel="noopener noreferrer" class="project-link">
                <svg class="icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                    <polyline points="15 3 21 3 21 9"></polyline>
                    <line x1="10" y1="14" x2="21" y2="3"></line>
                </svg>
                デモ
            </a>
        `;
    }

    card.innerHTML = `
        <div class="project-header">
            <h3 class="project-title">${project.title}</h3>
        </div>
        <p class="project-description">${project.description}</p>
        <div class="project-tech">
            ${project.tech.map(tech => `<span class="project-tech-tag">${tech}</span>`).join('')}
        </div>
        ${linksHTML ? `<div class="project-links">${linksHTML}</div>` : ''}
    `;

    return card;
}

// プロジェクトを表示
function renderProjects() {
    const projectsGrid = document.getElementById('projects-grid');
    if (!projectsGrid) return;

    projectsData.forEach(project => {
        const card = createProjectCard(project);
        projectsGrid.appendChild(card);
    });
}

// スムーススクロール
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const offsetTop = target.offsetTop - 80;
            window.scrollTo({
                top: offsetTop,
                behavior: 'smooth'
            });
        }
    });
});

// ナビゲーションのアクティブ状態
window.addEventListener('scroll', () => {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-menu a');
    
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop - 100;
        if (window.scrollY >= sectionTop) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
});

// スクロールアニメーション
function initScrollAnimation() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);

    // アニメーション対象の要素を監視
    document.querySelectorAll('.skill-category, .project-card, .contact-item').forEach(el => {
        el.classList.add('fade-in');
        observer.observe(el);
    });
}

// ページ読み込み時にプロジェクトを表示
document.addEventListener('DOMContentLoaded', () => {
    renderProjects();
    // 少し遅延させてスクロールアニメーションを初期化
    setTimeout(initScrollAnimation, 100);
});

