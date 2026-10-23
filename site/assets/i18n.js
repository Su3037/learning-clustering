// Page language for every script, including the engines (which must also run under Node for the tests: there it is 'zh').
// Chinese pages live at the original paths; English pages mirror them under en/ with <html lang="en">.
export const LANG = typeof document !== 'undefined' && document.documentElement?.lang?.startsWith('en') ? 'en' : 'zh';
/** Pick the string for the page language: L('中文', 'English'). Falls back to Chinese when no English is given. */
export const L = (zh, en) => (LANG === 'en' && en != null ? en : zh);
