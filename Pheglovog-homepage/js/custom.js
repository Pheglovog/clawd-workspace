// 自定义 JavaScript - Pheglovog 博客

// 阅读时间计算
function calculateReadingTime() {
  const content = document.querySelector('.geekdoc-content');
  if (!content) return;

  const text = content.textContent;
  const wordsPerMinute = 200; // 中文每分钟阅读字数
  const wordCount = text.length;
  const readingTime = Math.ceil(wordCount / wordsPerMinute);

  const timeElement = document.createElement('div');
  timeElement.className = 'reading-time';
  timeElement.innerHTML = `📖 ${readingTime} 分钟阅读`;

  const metaElement = document.querySelector('.post-meta');
  if (metaElement) {
    metaElement.appendChild(timeElement);
  }
}

// 搜索功能
function initSearch() {
  const searchInput = document.getElementById('search-input');
  if (!searchInput) return;

  const searchBox = document.createElement('div');
  searchBox.className = 'search-container';

  const input = document.createElement('input');
  input.type = 'text';
  input.id = 'search-input';
  input.className = 'search-box';
  input.placeholder = '🔍 搜索文章...';

  searchBox.appendChild(input);

  const nav = document.querySelector('.geekdoc-header');
  if (nav) {
    nav.appendChild(searchBox);
  }

  // 加载搜索索引
  fetch('/index.json')
    .then(response => response.json())
    .then(data => {
      window.searchIndex = data;
    })
    .catch(console.error);

  // 搜索事件
  input.addEventListener('input', (e) => {
    const query = e.target.value.toLowerCase();
    const results = window.searchIndex.filter(item =>
      item.title.toLowerCase().includes(query) ||
      item.content.toLowerCase().includes(query)
    );
    displaySearchResults(results);
  });
}

function displaySearchResults(results) {
  const searchResults = document.getElementById('search-results');
  if (!searchResults) return;

  searchResults.innerHTML = '';

  if (results.length === 0) {
    searchResults.innerHTML = '<p>没有找到匹配的文章</p>';
    return;
  }

  results.forEach(item => {
    const link = document.createElement('a');
    link.href = item.permalink;
    link.className = 'search-result-link';
    link.textContent = item.title;
    searchResults.appendChild(link);
  });
}

// 分享功能
function initShareButtons() {
  const shareButtons = document.querySelector('.share-buttons');
  if (!shareButtons) return;

  const url = window.location.href;
  const title = document.title;

  const shareLinks = [
    {
      name: 'Twitter',
      url: `https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(url)}`
    },
    {
      name: 'Facebook',
      url: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`
    },
    {
      name: 'LinkedIn',
      url: `https://www.linkedin.com/shareArticle?mini=true&url=${encodeURIComponent(url)}&title=${encodeURIComponent(title)}`
    },
    {
      name: '复制链接',
      action: () => {
        navigator.clipboard.writeText(url);
        alert('链接已复制到剪贴板！');
      }
    }
  ];

  shareLinks.forEach(link => {
    const btn = document.createElement('button');
    btn.className = 'share-btn';
    btn.textContent = link.name;

    if (link.url) {
      btn.onclick = () => window.open(link.url, '_blank', 'width=600,height=400');
    } else if (link.action) {
      btn.onclick = link.action;
    }

    shareButtons.appendChild(btn);
  });
}

// 评论系统初始化
function initComments() {
  // 使用 Giscus（基于 GitHub Discussions）
  const script = document.createElement('script');
  script.src = 'https://giscus.app/client.js';
  script.async = true;
  script.crossOrigin = 'anonymous';

  // 需要配置仓库
  script.setAttribute('data-repo', 'Pheglovog/pheglovog-site');
  script.setAttribute('data-repo-id', '');
  script.setAttribute('data-category', 'Announcements');
  script.setAttribute('data-category-id', '');
  script.setAttribute('data-mapping', 'pathname');
  script.setAttribute('data-strict', '0');
  script.setAttribute('data-reactions-enabled', '1');
  script.setAttribute('data-emit-metadata', '0');
  script.setAttribute('data-input-position', 'bottom');
  script.setAttribute('data-theme', 'dark');
  script.setAttribute('data-lang', 'zh-CN');

  const commentsSection = document.querySelector('.comments-section');
  if (commentsSection) {
    commentsSection.appendChild(script);
  }
}

// 目录高亮
function initTocHighlight() {
  const tocLinks = document.querySelectorAll('.geekdoc-toc a');
  const headings = document.querySelectorAll('.geekdoc-content h1, .geekdoc-content h2, .geekdoc-content h3');

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute('id');
        tocLinks.forEach(link => {
          if (link.getAttribute('href') === `#${id}`) {
            link.classList.add('active');
          } else {
            link.classList.remove('active');
          }
        });
      }
    });
  }, { threshold: 0.3 });

  headings.forEach(heading => observer.observe(heading));
}

// 平滑滚动
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
}

// 回到顶部
function initBackToTop() {
  const btn = document.createElement('button');
  btn.id = 'back-to-top';
  btn.innerHTML = '↑';
  btn.style.cssText = `
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: var(--primary-color);
    color: white;
    border: none;
    cursor: pointer;
    font-size: 1.5rem;
    opacity: 0;
    transition: opacity 0.3s;
    z-index: 1000;
  `;

  document.body.appendChild(btn);

  window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
      btn.style.opacity = '1';
    } else {
      btn.style.opacity = '0';
    }
  });

  btn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

// 页面加载完成
document.addEventListener('DOMContentLoaded', () => {
  calculateReadingTime();
  initSearch();
  initShareButtons();
  initTocHighlight();
  initSmoothScroll();
  initBackToTop();

  // 评论系统需要先配置 Giscus
  // initComments();
});

// 页面可见性变化
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    document.title = '👀 回来继续阅读！';
  } else {
    document.title = 'Pheglovog';
  }
});
