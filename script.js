// Navbar scroll effect
window.addEventListener('scroll', () => {
  const navbar = document.querySelector('.navbar');
  if (window.scrollY > 50) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
});

// Swiper Configuration
const swiper = new Swiper('.mySwiper', {
  navigation: {
    nextEl: '.swiper-button-next',
    prevEl: '.swiper-button-prev'
  },
  autoplay: {
    delay: 5000,
    disableOnInteraction: false
  },
  loop: true,
  effect: 'fade',
  speed: 800,
});

// Timeline Animation
const timelineItems = document.querySelectorAll('.timeline-item');
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
    }
  });
}, {
  threshold: 0.5
});

timelineItems.forEach(item => observer.observe(item));

// Local QA Widget
const qaState = {
  intents: [],
  fallback: [],
  typing: false,
};

const qaElements = {
  fab: document.getElementById('qaFab'),
  panel: document.getElementById('qaPanel'),
  close: document.getElementById('qaClose'),
  messages: document.getElementById('qaMessages'),
  input: document.getElementById('qaInput'),
  send: document.getElementById('qaSend')
};

const qaStopwords = new Set([
  'the', 'a', 'an', 'is', 'are', 'of', 'to', 'in', 'on', 'for', 'with', 'and',
  'or', 'what', 'how', 'why', 'when', 'where', 'does', 'do', 'can', 'could',
  'should', 'would', 'tell', 'me', 'about', 'explain', 'please'
]);

const qaReplacements = [
  ['least significant bit', 'lsb'],
  ['lsb method', 'lsb'],
  ['multi bit', 'multi-bit'],
  ['bit plane', 'bit-plane'],
  ['steganalysis', 'detection'],
  ['steganography', 'stego'],
  ['frequency domain', 'dct'],
  ['spatial domain', 'lsb']
];

const qaCommonMisspellings = {
  wat: 'what',
  wut: 'what',
  wht: 'what',
  lsb: 'lsb',
  stego: 'stego',
  stegano: 'stego',
  steganography: 'stego',
  stegnography: 'stego',
  steganograhy: 'stego',
  detction: 'detection',
  detecton: 'detection',
  capcity: 'capacity',
  capicity: 'capacity',
  algorithim: 'algorithm',
  algorthm: 'algorithm'
};

const qaMaxQueryLength = 200;

const qaQuickReplies = {
  empty: "Please enter a steganography question, like 'What is LSB?'",
  tooLong: "That is a bit long. Try a shorter question about LSB, detection, or history.",
  unknown: "Sorry, I can help with steganography, LSB methods, capacity, detection, and history. Try asking about LSB steps or LSB vs DCT."
};

function qaNormalize(text) {
  return text.toLowerCase().replace(/[^a-z0-9\s-]/g, ' ').replace(/\s+/g, ' ').trim();
}

function qaTokenize(text) {
  return qaNormalize(text)
    .split(' ')
    .filter(word => word && !qaStopwords.has(word));
}

function qaReformulate(query) {
  let reformulated = qaNormalize(query);
  qaReplacements.forEach(([from, to]) => {
    reformulated = reformulated.replace(new RegExp(from, 'g'), to);
  });
  reformulated = reformulated
    .split(' ')
    .map(word => qaCommonMisspellings[word] || word)
    .join(' ');
  return reformulated;
}

function qaEditDistance(a, b) {
  const alen = a.length;
  const blen = b.length;
  if (!alen) return blen;
  if (!blen) return alen;

  const dp = Array.from({ length: alen + 1 }, () => new Array(blen + 1).fill(0));
  for (let i = 0; i <= alen; i++) dp[i][0] = i;
  for (let j = 0; j <= blen; j++) dp[0][j] = j;

  for (let i = 1; i <= alen; i++) {
    for (let j = 1; j <= blen; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      dp[i][j] = Math.min(
        dp[i - 1][j] + 1,
        dp[i][j - 1] + 1,
        dp[i - 1][j - 1] + cost
      );
    }
  }

  return dp[alen][blen];
}

function qaClassify(query) {
  const q = qaNormalize(query);
  if (q.includes('compare') || q.includes('vs') || q.includes('difference')) {
    return 'comparison';
  }
  if (q.startsWith('how') || q.includes('steps') || q.includes('algorithm')) {
    return 'procedure';
  }
  if (q.startsWith('why') || q.includes('reason')) {
    return 'explanation';
  }
  if (q.includes('history') || q.includes('origin')) {
    return 'history';
  }
  if (q.includes('benefit') || q.includes('advantage') || q.includes('pros')) {
    return 'benefits';
  }
  if (q.includes('limitation') || q.includes('disadvantage') || q.includes('weakness')) {
    return 'limitations';
  }
  if (q.includes('detect') || q.includes('steganalysis')) {
    return 'detection';
  }
  return 'definition';
}

function qaScoreIntent(tokens, pattern) {
  const patternTokens = qaTokenize(pattern);
  if (!patternTokens.length) return 0;
  const matchCount = patternTokens.filter(token => {
    if (tokens.includes(token)) return true;
    if (token.length <= 3) return false;
    return tokens.some(candidate => qaEditDistance(candidate, token) <= 1);
  }).length;
  return matchCount / patternTokens.length;
}

function qaFindBestIntent(query) {
  const tokens = qaTokenize(query);
  let best = { intent: null, score: 0 };

  qaState.intents.forEach(intent => {
    intent.patterns.forEach(pattern => {
      const score = qaScoreIntent(tokens, pattern);
      if (score > best.score) {
        best = { intent, score };
      }
    });
  });

  return best.score >= 0.4 ? best.intent : null;
}

function qaPickResponse(intent) {
  const pool = intent ? intent.responses : qaState.fallback;
  return pool[Math.floor(Math.random() * pool.length)];
}

function qaNormalizeResponse(response) {
  if (typeof response === 'string') {
    return { text: response };
  }
  return response || { text: qaQuickReplies.unknown };
}

function qaTypeMessage(target, text, done) {
  let index = 0;
  const speed = 18;
  const timer = setInterval(() => {
    target.textContent += text[index];
    index += 1;
    if (index >= text.length) {
      clearInterval(timer);
      if (done) done();
    }
  }, speed);
}

function qaAddMessage(payload, type, meta, options = {}) {
  if (!qaElements.messages) return;
  const wrapper = document.createElement('div');
  wrapper.className = `qa-bubble ${type}`;

  const content = document.createElement('div');
  content.className = 'qa-text';
  wrapper.appendChild(content);

  const response = typeof payload === 'string' ? { text: payload } : qaNormalizeResponse(payload);
  const text = response.text || '';

  if (type === 'bot' && options.typing) {
    wrapper.classList.add('typing');
    qaTypeMessage(content, text, () => {
      wrapper.classList.remove('typing');
      if (response.bullets && response.bullets.length) {
        const list = document.createElement('ul');
        list.className = 'qa-bullets';
        response.bullets.forEach(item => {
          const li = document.createElement('li');
          li.textContent = item;
          list.appendChild(li);
        });
        wrapper.appendChild(list);
      }
      if (response.links && response.links.length) {
        const linkRow = document.createElement('div');
        linkRow.className = 'qa-links';
        response.links.forEach(link => {
          const anchor = document.createElement('a');
          anchor.className = 'qa-link';
          anchor.href = link.url;
          anchor.target = link.url.startsWith('http') ? '_blank' : '_self';
          anchor.rel = link.url.startsWith('http') ? 'noopener noreferrer' : '';
          anchor.textContent = link.label;
          linkRow.appendChild(anchor);
        });
        wrapper.appendChild(linkRow);
      }
      if (meta) {
        const metaDiv = document.createElement('div');
        metaDiv.className = 'qa-meta';
        metaDiv.textContent = meta;
        wrapper.appendChild(metaDiv);
      }
    });
  } else {
    content.textContent = text;
    if (response.bullets && response.bullets.length) {
      const list = document.createElement('ul');
      list.className = 'qa-bullets';
      response.bullets.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        list.appendChild(li);
      });
      wrapper.appendChild(list);
    }
    if (response.links && response.links.length) {
      const linkRow = document.createElement('div');
      linkRow.className = 'qa-links';
      response.links.forEach(link => {
        const anchor = document.createElement('a');
        anchor.className = 'qa-link';
        anchor.href = link.url;
        anchor.target = link.url.startsWith('http') ? '_blank' : '_self';
        anchor.rel = link.url.startsWith('http') ? 'noopener noreferrer' : '';
        anchor.textContent = link.label;
        linkRow.appendChild(anchor);
      });
      wrapper.appendChild(linkRow);
    }
  }

  if (meta && !(type === 'bot' && options.typing)) {
    const metaDiv = document.createElement('div');
    metaDiv.className = 'qa-meta';
    metaDiv.textContent = meta;
    wrapper.appendChild(metaDiv);
  }

  qaElements.messages.appendChild(wrapper);
  qaElements.messages.scrollTop = qaElements.messages.scrollHeight;
}

function qaHandleQuery() {
  const query = qaElements.input.value.trim();
  const normalized = qaNormalize(query);

  if (!normalized) {
    qaAddMessage(qaQuickReplies.empty, 'bot', 'Type: edge-case | Reformulated: ""', { typing: true });
    qaElements.input.value = '';
    return;
  }

  if (query.length > qaMaxQueryLength) {
    qaAddMessage(qaQuickReplies.tooLong, 'bot', 'Type: edge-case | Reformulated: ""', { typing: true });
    qaElements.input.value = '';
    return;
  }

  qaAddMessage(query, 'user');

  const reformulated = qaReformulate(query);
  const answerType = qaClassify(query);
  const matched = qaFindBestIntent(reformulated);
  const response = matched ? qaPickResponse(matched) : { text: qaQuickReplies.unknown };

  const meta = `Type: ${answerType} | Reformulated: "${reformulated}"`;
  qaAddMessage(response, 'bot', meta, { typing: true });

  qaElements.input.value = '';
}

function qaToggle(open) {
  if (!qaElements.panel) return;
  const isOpen = open ?? !qaElements.panel.classList.contains('open');
  qaElements.panel.classList.toggle('open', isOpen);
  qaElements.panel.setAttribute('aria-hidden', isOpen ? 'false' : 'true');
  if (isOpen && qaElements.input) {
    qaElements.input.focus();
  }
}

async function qaInit() {
  if (!qaElements.fab || !qaElements.panel) return;
  try {
    if (window.QA_INTENTS) {
      qaState.intents = window.QA_INTENTS.intents || [];
      qaState.fallback = window.QA_INTENTS.fallback || ["Try asking about LSB or steganography."];
    } else {
      const res = await fetch('qa_intents.json');
      const data = await res.json();
      qaState.intents = data.intents || [];
      qaState.fallback = data.fallback || ["Try asking about LSB or steganography."];
    }
  } catch (err) {
    qaState.intents = [];
    qaState.fallback = ["Local intents unavailable. Please try again later."];
  }

  qaElements.fab.addEventListener('click', () => qaToggle(true));
  qaElements.close.addEventListener('click', () => qaToggle(false));
  qaElements.send.addEventListener('click', qaHandleQuery);
  qaElements.input.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
      qaHandleQuery();
    }
  });

  qaAddMessage(
    'Hi! Ask me about steganography, LSB methods, capacity, detection, or history.',
    'bot',
    'Type: greeting | Reformulated: "steganography lsb overview"',
    { typing: true }
  );
}

qaInit();
