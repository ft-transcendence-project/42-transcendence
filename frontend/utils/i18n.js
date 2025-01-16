i18next
  .use(i18nextHttpBackend)
  .use(i18nextBrowserLanguageDetector) // ブラウザの言語設定を取得
  .init({
    fallbackLng: 'en', // ブラウザの言語が取得できない場合のデフォルト言語
    debug: false,
    ns: ['navbar', 'home', 'login', 'signup', 'tournament', 'matches', 'gamesetting', 
    'logout', 'setupotp', 'verifyotp', 'gameplay', 'winner'], // 翻訳キーの名前空間
    backend: {
      loadPath: './utils/locales/{{lng}}/{{ns}}.json', // 見つからない場合fallbackLngを参照
    },
    detection: {
      // 言語検出の順序を設定
      order: ['cookie', 'navigator'],
      lookupCookie: 'default_language', // cookieのキー名を指定
      caches: [], // キャッシュしない
    },
  }, (err, t) => {
    if (err) return console.error('i18next init error:', err);
    updateContent(); // 初期翻訳適用
  });

export function updateContent() {
  // data-i18n属性を持つ全ての要素を翻訳キーを元に翻訳
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    
    // 属性の翻訳（[attr]key形式）
    if (key.includes('[')) {
      const matches = key.match(/\[(.*?)\](.*)/);
      if (matches) {
        const attr = matches[1];
        const translationKey = matches[2];
        el.setAttribute(attr, i18next.t(translationKey));
      }
    } else {
      if (el.children.length > 0) {
        // 子要素を持つ場合
        const childElements = Array.from(el.children).map(child => child.outerHTML);
        const translatedText = i18next.t(key);
        el.innerHTML = DOMPurify.sanitize(translatedText + childElements.join(''));
      } else {
        // 通常のテキスト翻訳
        el.textContent = i18next.t(key);
      }
    }
  });
}

export function changeLanguage(lng) {
  i18next.changeLanguage(lng); // 言語設定を変更し、languageChangedイベント
}

// languageChangedイベントによりトリガー
i18next.on('languageChanged', () => {
  updateContent();
});
