/**
 * Parser for the legacy Gemini resume-analysis text (Backend/fastapi_app/
 * Internship|Placement/gemini_resume_*.py's prompt contract). Verified
 * against real output across multiple runs — the LLM does not always
 * follow its own formatting instructions exactly: the "(A)" letter
 * markers are sometimes dropped, a section title sometimes shares its
 * line with the start of its paragraph ("Education: The resume...")
 * and sometimes doesn't ("Education\nThe resume..."), bullets vary
 * between "-", "*", "•", and markdown bold wrapping around block labels
 * ("**Critical Errors:**") leaves stray asterisks at slice boundaries.
 * This parses structurally and defensively rather than depending on one
 * exact format.
 *
 * Never sent to an LLM a second time — this is pure string parsing of
 * a response the backend already returned.
 */

function cleanParagraph(text) {
  return text.replace(/\s+/g, ' ').trim();
}

/** Strips markdown/bullet noise stray at slice boundaries (a lone `*`
 * left over from an adjacent "**Header:**" wrapper, a leftover bullet
 * marker) before attempting to split "**Title**: body". */
function splitTitleBody(text) {
  let trimmed = text.replace(/^[\s•-]+/, '');
  // A single leftover asterisk (not part of a **bold** pair) can precede
  // the real content when a slice boundary lands between the two
  // asterisks of an adjacent "**Header:**" wrapper — strip just that one,
  // never a genuine "**" pair.
  if (/^\*(?!\*)/.test(trimmed)) trimmed = trimmed.replace(/^\*/, '').trim();
  trimmed = trimmed.replace(/[\s*]+$/, '');

  const match = trimmed.match(/^\*\*(.+?)\*\*:?\s*(.*)$/s);
  if (match) return { title: cleanParagraph(match[1]).replace(/:$/, ''), body: cleanParagraph(match[2]) };
  return { title: null, body: cleanParagraph(trimmed) };
}

/** Classifies one line of the section-analysis block as either a new
 * section header or a body continuation. Handles both observed shapes:
 * a short standalone title line ("Contact Information"), and a title
 * sharing its line with the start of the paragraph ("Contact
 * Information: The resume provides..."). */
function classifySectionLine(line) {
  const colonMatch = line.match(/^\(?([A-Z])?\)?\s*([A-Z][A-Za-z\/&+,.\- ]{1,45}?):\s*(.*)$/);
  if (colonMatch && cleanParagraph(colonMatch[2]).split(' ').length <= 6) {
    return { letter: colonMatch[1], title: cleanParagraph(colonMatch[2]), body: cleanParagraph(colonMatch[3]) };
  }
  if (!line.includes(':') && !/[.!?]$/.test(line) && line.split(/\s+/).length <= 8) {
    const wholeMatch = line.match(/^\(?([A-Z])?\)?\s*([A-Z][A-Za-z\/&+,.\- ]{1,55})$/);
    if (wholeMatch) return { letter: wholeMatch[1], title: cleanParagraph(wholeMatch[2]), body: '' };
  }
  return null;
}

function parseSections(text) {
  const lines = text.split('\n');
  const sections = [];
  let current = null;
  let letterIndex = 0;

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) continue;
    if (/SECTION-BY-SECTION ANALYSIS/i.test(line) || /^#+\s*#?FINAL OUTPUT/i.test(line) || /^#+\s*$/.test(line)) continue;

    const header = classifySectionLine(line);
    if (header) {
      if (current && current.body) sections.push(current);
      const letter = header.letter || String.fromCharCode(65 + letterIndex);
      letterIndex += 1;
      current = { letter, title: header.title.replace(/[:.]$/, ''), body: header.body };
    } else if (current) {
      current.body = current.body ? `${current.body} ${line}` : line;
    }
  }
  if (current && current.body) sections.push(current);
  return sections;
}

function parseScores(text) {
  const scores = [];
  const scoreLineRegex = /([A-Za-z][A-Za-z \/&+,-]*?):\s*(\d+)\s*\/\s*(\d+)\.?/g;
  let match;
  while ((match = scoreLineRegex.exec(text)) !== null) {
    const [, label, value, max] = match;
    if (parseInt(max, 10) <= 0) continue; // "Summary/Objective: 0/0" — ungraded, nothing to show
    scores.push({ label: cleanParagraph(label), value: parseInt(value, 10), max: parseInt(max, 10) });
  }
  return scores;
}

function parseNumberedList(text) {
  const items = [];
  const regex = /\d+\.\s+([\s\S]*?)(?=\n\s*\d+\.\s|$)/g;
  let match;
  while ((match = regex.exec(text)) !== null) {
    const { title, body } = splitTitleBody(match[1]);
    if (title || body) items.push({ title, body });
  }
  return items;
}

function parseBulletList(text) {
  const items = [];
  const regex = /[-*•]\s+([\s\S]*?)(?=\n\s*[-*•]\s|$)/g;
  let match;
  while ((match = regex.exec(text)) !== null) {
    const { title, body } = splitTitleBody(match[1]);
    if (title || body) items.push({ title, body });
  }
  return items;
}

export function parseGeminiResult(raw) {
  if (!raw) return null;

  const overallMatch = raw.match(/Overall Score\*{0,2}\s*[=:]?\s*(\d+)\s*\/\s*100/i);
  const overallScore = overallMatch ? Math.max(0, Math.min(100, parseInt(overallMatch[1], 10))) : null;

  const blockBounds = ['Section-wise Scores', 'Personalized Suggestions', 'Critical Errors'];
  const indices = blockBounds.map((label) => {
    const m = raw.match(new RegExp(label, 'i'));
    return m ? m.index : -1;
  });

  const sectionAnalysisText = raw.slice(0, indices[0] > -1 ? indices[0] : indices.find((i) => i > -1) ?? raw.length);
  const scoresText = indices[0] > -1 ? raw.slice(indices[0], indices[1] > -1 ? indices[1] : indices[2] > -1 ? indices[2] : raw.length) : '';
  const suggestionsText = indices[1] > -1 ? raw.slice(indices[1], indices[2] > -1 ? indices[2] : raw.length) : '';
  const errorsText = indices[2] > -1 ? raw.slice(indices[2]) : '';

  return {
    overallScore,
    sections: parseSections(sectionAnalysisText),
    scores: parseScores(scoresText),
    suggestions: parseNumberedList(suggestionsText),
    criticalErrors: parseBulletList(errorsText),
    raw,
  };
}
