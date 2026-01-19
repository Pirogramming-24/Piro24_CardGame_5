const step1 = document.getElementById("step1");
const step2 = document.getElementById("step2");
const step3 = document.getElementById("step3");

const defenderSelect = document.getElementById("defenderSelect");
const drawBtn = document.getElementById("drawBtn");
const cardRow = document.getElementById("cardRow");

const selectedCardInput = document.getElementById("selectedCardInput");
const selectedCardNum = document.getElementById("selectedCardNum");
const finalCardDisplay = document.getElementById("finalCardDisplay");

// 서버에서 받은 데이터 사용
let pickedNumbers = window.randomCards || []; 

// [STEP 1] 상대 선택 시 버튼 활성화
if (defenderSelect) {
    defenderSelect.addEventListener("change", (e) => {
        if(drawBtn) drawBtn.disabled = !e.target.value;
    });
}

// [STEP 2] DRAW 버튼 클릭 -> 애니메이션 시작
if (drawBtn) {
    drawBtn.addEventListener("click", () => {
        step1.classList.add("hidden");
        step2.classList.remove("hidden");

        // 1. 10장 렌더링 (등장 애니메이션)
        renderTenCards();

        // 2. 1.5초 후 유효한 5장만 활성화 (내려오는 애니메이션)
        setTimeout(() => {
            markPickedCards(pickedNumbers);
        }, 1500);
    });
}

function renderTenCards() {
    cardRow.innerHTML = "";

    for (let n = 1; n <= 10; n++) {
        const btn = document.createElement("button");
        btn.type = "button";
        // card-enter: 등장 애니메이션 클래스 (CSS 필요)
        btn.className = "card-btn dim card-enter"; 
        btn.dataset.value = String(n);
        
        // 0.1초 간격으로 순차 등장
        btn.style.animationDelay = `${n * 0.1}s`;

        const img = document.createElement("img");
        // ★ 수정됨: Django static 경로 활용
        img.src = `${window.CARD_BASE_URL}card${n}.jpg`;
        img.alt = `card ${n}`;

        btn.appendChild(img);
        cardRow.appendChild(btn);
    }
}

function markPickedCards(numbers) {
    const allBtns = cardRow.querySelectorAll(".card-btn");

    allBtns.forEach((btn) => {
        const n = Number(btn.dataset.value);

        // 등장 애니메이션 클래스 제거 (상태 고정)
        btn.classList.remove("card-enter");
        btn.style.animation = "none"; 

        if (numbers.includes(n)) {
            // [활성화 카드] dim 제거 -> picked 추가 (CSS transition으로 내려옴)
            btn.classList.remove("dim");
            btn.classList.add("picked");

            btn.onclick = function() {
                handleCardClick(this, n);
            };
        } else {
            // [비활성화 카드] 계속 dim 유지
            btn.classList.add("dim");
            btn.style.cursor = "not-allowed";
        }
    });
}

function handleCardClick(clickedBtn, n) {
    // 선택되지 않은 다른 picked 카드들은 다시 dim 처리
    const allPicked = cardRow.querySelectorAll(".picked");
    allPicked.forEach(b => {
        if(b !== clickedBtn) {
            b.classList.remove("picked");
            b.classList.add("dim");
            b.style.transform = "translateY(0) scale(1)"; // 위치 복귀
        }
    });

    // 데이터 저장
    if(selectedCardInput) selectedCardInput.value = n;
    if(selectedCardNum) selectedCardNum.innerText = n;

    // 0.6초 뒤 다음 단계 이동
    setTimeout(() => {
        step2.classList.add("hidden");
        step3.classList.remove("hidden");
    }, 600);

    // 이미지 복사
    if(finalCardDisplay) {
        finalCardDisplay.innerHTML = clickedBtn.innerHTML;
        const img = finalCardDisplay.querySelector('img');
        if (img) img.className = 'selected-img';
    }
}