let notificationTimeout;
let pendingUsername = null;
let pendingButton = null;
let pendingPostLink = null;

function updateEksiklerCount(index) {
    const list = document.getElementById(`eksiklerListesi-${index}`);
    const badge = document.getElementById(`elemanSayisi-${index}`);
    if (!list || !badge) return;
    const items = Array.from(list.getElementsByTagName("li"));
    const visibleCount = items.filter((item) => item.style.display !== "none").length;
    badge.innerText = `Eksik: ${visibleCount}`;
}

function showNotification(message) {
    const notification = document.getElementById("notification");
    document.getElementById("notification-message").innerText = message;

    if (notification.classList.contains("visible")) {
        clearTimeout(notificationTimeout);
        notification.classList.remove("visible");
    }

    notification.style.display = "block";
    setTimeout(() => {
        notification.classList.add("visible");
    }, 10);

    notificationTimeout = setTimeout(() => {
        notification.classList.remove("visible");
    }, 3000);
}

function closeModal() {
    document.getElementById("confirmModal").classList.remove("show");
    pendingUsername = null;
    pendingButton = null;
    pendingPostLink = null;
}

function addExemption(username, postLink, button) {
    pendingUsername = username;
    pendingButton = button;
    pendingPostLink = postLink;
    document.getElementById("modalUsername").textContent = `@${username}`;
    document.getElementById("confirmModal").classList.add("show");
}

function confirmExemption() {
    if (!pendingUsername || !pendingButton || !pendingPostLink) {
        return;
    }

    const username = pendingUsername;
    const button = pendingButton;
    const postLink = pendingPostLink;
    closeModal();

    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Kaydediliyor...';

    fetch("/add_exemption", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ post_link: postLink, username }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                const listItem = button.closest("li");
                const parentList = listItem && listItem.parentElement;
                const listId = parentList && parentList.id;
                const indexPart = listId ? listId.split("-").pop() : null;
                const idx = indexPart ? parseInt(indexPart, 10) : null;

                listItem.style.transition = "all 0.3s ease";
                listItem.style.opacity = "0";
                listItem.style.transform = "translateX(20px)";

                setTimeout(() => {
                    listItem.remove();
                    if (idx) updateEksiklerCount(idx);
                    showNotification(`@${username} izinli listesine eklendi!`);
                }, 300);
                return;
            }

            showNotification(`Hata: ${data.message}`);
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-check me-1"></i>Izinli Say';
        })
        .catch(() => {
            showNotification("Bir hata olustu!");
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-check me-1"></i>Izinli Say';
        });
}

function fallbackCopyToClipboard(text, count) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed";
    textArea.style.left = "-9999px";
    textArea.style.top = "0";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
        const successful = document.execCommand("copy");
        showNotification(successful ? `Liste kopyalandi! Toplam eksik sayisi: ${count}` : "Kopyalama basarisiz oldu!");
    } catch (_error) {
        showNotification("Kopyalama desteklenmiyor!");
    }

    document.body.removeChild(textArea);
}

function kopyalaListeyiFrom(listElementId, label) {
    const list = document.getElementById(listElementId);
    if (!list) return;
    const listItems = list.getElementsByTagName("li");
    let text = "";

    for (let i = 0; i < listItems.length; i += 1) {
        const username = listItems[i].getAttribute("data-username");
        if (username) {
            text += `@${username}`;
            if (i < listItems.length - 1) {
                text += "\n";
            }
        }
    }

    const count = listItems.length;
    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text)
            .then(() => showNotification(`Liste kopyalandi! Toplam ${label} sayisi: ${count}`))
            .catch(() => fallbackCopyToClipboard(text, count));
        return;
    }

    fallbackCopyToClipboard(text, count);
}

function copyEksiklerList(index) {
    kopyalaListeyiFrom(`eksiklerListesi-${index}`, "eksik");
}

function copyCompletedList() {
    kopyalaListeyiFrom("completedList", "tamamlamis kullanici");
}

function filterEksiklerList(index) {
    const list = document.getElementById(`eksiklerListesi-${index}`);
    if (!list) return;
    
    const card = list.closest('.link-card');
    if (!card) return;
    
    const inputEl = card.querySelector(".search-input");
    const input = inputEl ? inputEl.value.toLowerCase() : "";
    const listItems = list.getElementsByTagName("li");

    for (let i = 0; i < listItems.length; i += 1) {

        const item = listItems[i];
        const textValue = item.innerText.toLowerCase();
        item.style.display = textValue.includes(input) ? "" : "none";
    }

    updateEksiklerCount(index);
}

function filterCompletedList() {
    const input = document.getElementById("completedSearchInput").value.toLowerCase();
    const list = document.getElementById("completedList");
    if (!list) return;
    const listItems = list.getElementsByTagName("li");

    for (let i = 0; i < listItems.length; i += 1) {
        const item = listItems[i];
        const textValue = item.innerText.toLowerCase();
        item.style.display = textValue.includes(input) ? "" : "none";
    }
}

window.addExemption = addExemption;
window.closeModal = closeModal;
window.confirmExemption = confirmExemption;
window.copyEksiklerList = copyEksiklerList;
window.copyCompletedList = copyCompletedList;
window.filterEksiklerList = filterEksiklerList;
window.filterCompletedList = filterCompletedList;
window.toggleCompletedSection = toggleCompletedSection;
window.toggleEksiklerSection = toggleEksiklerSection;
window.copyLink = copyLink;
window.refreshResults = refreshResults;

function toggleCompletedSection() {
    const section = document.getElementById("completedSection");
    const icon = document.getElementById("completedSectionIcon");
    if (section.style.display === "none") {
        section.style.display = "block";
        icon.style.transform = "rotate(180deg)";
    } else {
        section.style.display = "none";
        icon.style.transform = "rotate(0deg)";
    }
}

function toggleEksiklerSection(index) {
    const section = document.getElementById(`eksiklerSection-${index}`);
    const icon = document.getElementById(`eksiklerIcon-${index}`);
    if (section.style.display === "none") {
        section.style.display = "block";
        icon.style.transform = "rotate(180deg)";
    } else {
        section.style.display = "none";
        icon.style.transform = "rotate(0deg)";
    }
}

function copyLink(link) {
    navigator.clipboard.writeText(link).then(() => {
        showNotification("Link kopyalandi!");
    }).catch(() => {
        showNotification("Link kopyalanamadi!");
    });
}

function copyUserMissingPosts(username) {
    const container = document.getElementById('missing-posts-' + username);
    if (!container) return;
    
    const links = [];
    container.querySelectorAll('a').forEach(a => {
        links.push(a.textContent);
    });
    
    const text = links.join('\n');
    navigator.clipboard.writeText(text).then(() => {
        showNotification("@" + username + " için " + links.length + " link kopyalandı!");
    }).catch(() => {
        showNotification("Kopyalama başarısız!");
    });
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification("Kopyalandı!");
    }).catch(() => {
        showNotification("Kopyalama başarısız!");
    });
}

function refreshResults() {
    const links = [];
    document.querySelectorAll('.eksikler-list').forEach(list => {
        const postLink = list.dataset.postLink;
        if (postLink && !links.includes(postLink)) {
            links.push(postLink);
        }
    });
    
    const groupUsers = [];
    document.querySelectorAll('.eksikler-list li').forEach(item => {
        const username = item.dataset.username;
        if (username && !groupUsers.includes(username)) {
            groupUsers.push(username);
        }
    });
    
    const allCommented = [];
    document.querySelectorAll('#completedList li').forEach(item => {
        const username = item.dataset.username;
        if (username) {
            allCommented.push(username);
        }
    });
    
    const allUsers = [...groupUsers, ...allCommented];
    
    if (links.length > 0) {
        const linkParam = encodeURIComponent(links.join('\n'));
        const groupParam = encodeURIComponent(allUsers.join(' '));
        window.location.href = `/?refresh=1&link=${linkParam}&group=${groupParam}`;
    }
}

window.onload = function onLoad() {
    const lists = document.querySelectorAll(".eksikler-list");
    lists.forEach((list, idx) => {
        const indexPart = list.id.split("-").pop();
        const index = parseInt(indexPart, 10);
        if (index) updateEksiklerCount(index);
    });
};
