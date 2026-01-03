const ALLOWED_WEB_VOICES = ['tingting', 'meijia'];

export const filterWebVoices = (
  voices: SpeechSynthesisVoice[],
  lang: string = 'zh-TW'
) => {
  const langPrefix = lang.split('-')[0];
  const allowed = voices.filter((voice) => {
    const name = `${voice.name} ${voice.voiceURI}`.toLowerCase();
    return ALLOWED_WEB_VOICES.some((allowedName) => name.includes(allowedName));
  });
  const langVoices = allowed.filter((voice) => voice.lang.startsWith(langPrefix));
  return langVoices.length > 0 ? langVoices : allowed;
};

export const pickWebVoice = (
  voices: SpeechSynthesisVoice[],
  preferredVoiceUri: string,
  lang: string = 'zh-TW'
) => {
  if (!voices.length) return null;
  if (preferredVoiceUri) {
    const preferred = voices.find((voice) => voice.voiceURI === preferredVoiceUri);
    if (preferred) return preferred;
  }
  const candidates = filterWebVoices(voices, lang);
  return candidates[0] ?? voices[0];
};
