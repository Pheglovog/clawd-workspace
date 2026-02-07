// 自定义 JavaScript - Pheglovog 博客
(() => {
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const originalTitle = document.title;

  const debounce = (fn, delay = 150) => {
    let timer;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => fn(...args), delay);
    };
  };

  // 阅读时间计算
  const calculateReadingTime = () => {
    const content = document.querySelector('.article-content');
    if (!content) return;

    const text = content.textContent?.trim() || '';
    if (!text) return;

    const wordsPerMinute = 200; // 中文每分钟阅读字数
    const wordCount = text.length;
    const readingTime = Math.max(1, Math.ceil(wordCount / wordsPerMinute));

    const timeElement = document.createElement('span');
    timeElement.className = 'reading-time';
    timeElement.textContent = ` · 📖 ${readingTime} 分钟阅读`;

    const metaElement = document.querySelector('.article-meta');
    if (metaElement) {
      metaElement.appendChild(timeElement);
    }
  };

  // 搜索功能
  const initSearch = () => {
    const searchRoot = document.querySelector('[data-search-root]');
    const resultsContainer = document.getElementById('search-results');
    if (!searchRoot || !resultsContainer) return;

    const searchBox = document.createElement('div');
    searchBox.className = 'search-container';

    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'search-box';
    input.placeholder = '🔍 搜索文章...';
    input.setAttribute('aria-label', '搜索文章');

    searchBox.appendChild(input);
    searchRoot.appendChild(searchBox);

    let searchIndex = [];
    fetch('/index.json')
      .then((response) => response.json())
      .then((data) => {
        searchIndex = Array.isArray(data) ? data : [];
      })
      .catch(() => {
        searchIndex = [];
      });

    const handleSearch = debounce((query) => {
      const normalized = query.trim().toLowerCase();
      if (!normalized) {
        displaySearchResults([]);
        return;
      }

      const results = searchIndex.filter((item) => {
        const title = (item.title || '').toLowerCase();
        const content = (item.content || '').toLowerCase();
        return title.includes(normalized) || content.includes(normalized);
      });
      displaySearchResults(results);
    });

    input.addEventListener('input', (event) => {
      handleSearch(event.target.value || '');
    });
  };

  const displaySearchResults = (results) => {
    const searchResults = document.getElementById('search-results');
    if (!searchResults) return;

    searchResults.innerHTML = '';

    if (!results.length) {
      searchResults.innerHTML = '<p>没有找到匹配的文章</p>';
      return;
    }

    results.forEach((item) => {
      const link = document.createElement('a');
      link.href = item.permalink;
      link.className = 'search-result-link';
      link.textContent = item.title;
      searchResults.appendChild(link);
    });
  };

  // 分享功能
  const initShareButtons = () => {
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
          if (navigator.clipboard?.writeText) {
            navigator.clipboard.writeText(url);
          }
        }
      }
    ];

    shareLinks.forEach((link) => {
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
  };

  // 评论系统初始化
  const initComments = () => {
    const commentsSection = document.querySelector('.comments-section');
    if (!commentsSection) return;

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
    script.setAttribute('data-theme', 'light');
    script.setAttribute('data-lang', 'zh-CN');

    commentsSection.appendChild(script);
  };

  // 目录高亮
  const initTocHighlight = () => {
    const tocLinks = document.querySelectorAll('.geekdoc-toc a');
    const headings = document.querySelectorAll('.article-content h1, .article-content h2, .article-content h3');
    if (!tocLinks.length || !headings.length) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const id = entry.target.getAttribute('id');
            tocLinks.forEach((link) => {
              if (link.getAttribute('href') === `#${id}`) {
                link.classList.add('active');
              } else {
                link.classList.remove('active');
              }
            });
          }
        });
      },
      { threshold: 0.3 }
    );

    headings.forEach((heading) => observer.observe(heading));
  };

  // 平滑滚动
  const initSmoothScroll = () => {
    if (prefersReducedMotion) return;
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener('click', function (event) {
        const target = document.querySelector(this.getAttribute('href'));
        if (!target) return;
        event.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });
  };

  // 回到顶部
  const initBackToTop = () => {
    const btn = document.createElement('button');
    btn.className = 'back-to-top';
    btn.setAttribute('type', 'button');
    btn.setAttribute('aria-label', '返回顶部');
    btn.textContent = '↑';

    document.body.appendChild(btn);

    window.addEventListener('scroll', () => {
      btn.classList.toggle('is-visible', window.scrollY > 300);
    });

    btn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: prefersReducedMotion ? 'auto' : 'smooth' });
    });
  };

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

  document.addEventListener('visibilitychange', () => {
    document.title = document.hidden ? '👀 回来继续阅读！' : originalTitle;
  });
})();
