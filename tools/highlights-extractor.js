highlights_ids = []
highlights_texts = []

notes_ids = []
notes_texts = []

function fixMissingFirstChar(highlightElement, extractedText) {
    page = highlightElement.closest('.page');
    if (!page) return extractedText;
    textLayer = page.querySelector('.textLayer');
    if (!textLayer) return extractedText;

    fullRaw = textLayer.innerText;
    fullNorm = fullRaw.replace(/\s+/g, ' ').trim();
    rawNorm = extractedText.replace(/\s+/g, ' ').trim();

    idx = fullNorm.indexOf(rawNorm);
    if (idx > 0) {
        prev = fullNorm[idx - 1];
        if (/[a-zA-Z]/.test(prev)) {
            return prev + extractedText;
        }
    }
    return extractedText;
}

function downloadJSON(data, filename = "highlights_notes.json") {
    jsonString = JSON.stringify(data, null, 2);
    blob = new Blob([jsonString], { type: "application/json" });
    url = URL.createObjectURL(blob);
    
    link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}



// ------------------------------------



highlights = document.querySelectorAll('section[class="highlightAnnotation"]')

for (let i = 0; i < highlights.length; i++) {
    id = highlights[i].getAttribute('data-annotation-id')
    if (!highlights_ids.includes(id)) {
        console.log(id)
        highlights_ids.push(id)

        rawText = highlights[i].querySelector('mark').innerText
        fixedText = fixMissingFirstChar(highlights[i], rawText)
        console.log(fixedText)
        highlights_texts.push(fixedText)
    }
}

notes = document.querySelectorAll('div[class="annotationTextContent"]')

for (let i = 0; i < notes.length; i++) {
    id = notes[i].getAttribute('id').replace('pdfjs_internal_id_', '')
    if (!notes_ids.includes(id)) {
        // exclude two notes with IDs '19244R' and '19253R'
        if (!['19244R', '19253R'].includes(id)) {
            console.log(id)
            notes_ids.push(id)

            // text = notes[i].innerText
            spans = notes[i].querySelectorAll('span');
            if (spans.length > 0) {
                text = Array.from(spans).map(span => span.innerText).join(' ');
            } else {
                text = notes[i].innerText;
            }
            console.log(text)
            notes_texts.push(text)
        }
    }
}



// ------------------------------------



data = []
for (let i = 0; i < highlights_ids.length; i++) {
    highlight_note = {}
    highlight_note['highlight_id'] = highlights_ids[i]
    highlight_note['highlight_text'] = highlights_texts[i]
    highlight_note['note_id'] = notes_ids[i]
    highlight_note['note_text'] = notes_texts[i]
    data.push(highlight_note)
}

downloadJSON(data);



// ------------------------------------



highlight_data = []
note_data = []
for (let i = 0; i < highlights_ids.length; i++) {
    highlight_obj = {}
    note_obj = {}
    highlight_obj['highlight_id'] = highlights_ids[i]
    highlight_obj['highlight_text'] = highlights_texts[i]
    note_obj['note_id'] = notes_ids[i]
    note_obj['note_text'] = notes_texts[i]
    highlight_data.push(highlight_obj)
    note_data.push(note_obj)
}

downloadJSON(highlight_data, "highlights_data.json");
downloadJSON(note_data, "note_data.json");