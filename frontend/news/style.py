# Inject CSS once
card_css = """
<style>
.card {
    background-color: white;
    border-radius: 10px;
    padding: 0px;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    width: 340px;
    height: 550px;
    font-family: 'Segoe UI', sans-serif;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}
.card img {
    width: 100%;
    height: 180px;
    object-fit: cover;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
}
.card .content {
    padding: 15px;
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    width: 100%;
}
.date-badge {
    background-color: #f44336;
    color: white;
    font-size: 12px;
    border-radius: 20px;
    padding: 10px;
    position: absolute;
    right: 15px;
    top: 15px;
    width: 100px;
    height: 30px;
    text-align: center;
    line-height: 10px;
}
.title {
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 5px;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
}
.subtitle {
    color: #e74c3c;
    font-size: 14px;
    margin-bottom: 10px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.description {
    font-size: 13px;
    color: #555;
    height: 120px;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 6;
    -webkit-box-orient: vertical;
    line-height: 1.4;
    margin-bottom: 10px;
}
.topic {
    font-size: 12px;
    color: #2c7be5;
    font-weight: bold;
    margin-bottom: 10px;
    background-color: #e8f4fd;
    padding: 4px 8px;
    border-radius: 12px;
    display: inline-block;
}
.keyword {
    font-size: 12px;
    color: #2c7be5;
    font-weight: bold;
    margin-right: 5px;
    background-color: #e8f4fd;
    padding: 4px 8px;
    border-radius: 12px;
    display: inline-block;
}
.meta {
    font-size: 12px;
    color: gray;
    margin-top: 10px;
}
.actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
}
.action-buttons {
    display: flex;
    gap: 10px;
    align-items: center;
}
a.visit-link {
    text-decoration: none;
    font-size: 13px;
    color: #2c7be5;
    margin-right: 100px;
}
.save-btn {
    background: none;
    border: none;
    font-size: 16px;
    cursor: pointer;
    padding: 4px;
}
.relevance-buttons {
    display: flex;
    gap: 5px;
    margin-top: 8px;
}
.relevance-btn {
    background: none;
    border: 1px solid #ddd;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.3s;
}
.relevance-btn.relevant {
    background-color: #28a745;
    color: white;
    border-color: #28a745;
}
.relevance-btn.not-relevant {
    background-color: #dc3545;
    color: white;
    border-color: #dc3545;
}
.relevance-btn:hover {
    opacity: 0.8;
}

.meta-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
    font-size: 13px;
}
.meta-info .visit-link {
    margin: 0;
}
.meta-info .topic {
    margin: 0;
}

</style>
"""


# JavaScript pour gérer les interactions
js_code = """
<script>
function toggleSave(link, cardId) {
    const saveBtn = document.getElementById('save_btn_' + cardId);
    const currentIcon = saveBtn.innerText;
    
    if (currentIcon === '💾') {
        // Sauvegarder
        saveBtn.innerText = '❌';
        // Ici vous pourriez faire un appel AJAX pour sauvegarder
        console.log('Saving:', link);
    } else {
        // Désauvegarder
        saveBtn.innerText = '💾';
        // Ici vous pourriez faire un appel AJAX pour désauvegarder
        console.log('Unsaving:', link);
    }
}

function markRelevant(link, cardId) {
    console.log('Marking as relevant:', link);
    // Vous pourriez faire un appel AJAX ici
    alert('Marked as relevant!');
}

function markNotRelevant(link, cardId) {
    const card = document.getElementById('card_' + cardId);
    if (confirm('Remove this article from your feed?')) {
        card.style.transition = 'opacity 0.5s';
        card.style.opacity = '0.5';
        console.log('Marking as not relevant:', link);
        // Vous pourriez faire un appel AJAX ici
        setTimeout(() => {
            card.style.display = 'none';
        }, 500);
    }
}
</script>
"""
