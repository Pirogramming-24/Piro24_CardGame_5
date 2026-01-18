const step1 = document.getElementById("step1");
const step2 = document.getElementById("step2");
const step3 = document.getElementById("step3");

const defenderSelect = document.getElementById("defenderSelect");
const drawBtn = document.getElementById("drawBtn");

const cardRow = document.getElementById("cardRow");

const selectedImg = document.getElementById("selectedImg");
const selectedText = document.getElementById("selectedText");

let defender = null;
let pickedNumbers = []; // 5장 숫자

// STEP1: defender 선택되면 버튼 활성화
defenderSelect.addEventListener("change", (e) => {
  defender = e.target.value;
  drawBtn.disabled = !defender;
  console.log("됨");
});

drawBtn.addEventListener("click", () => {
  // 1) step1 숨기고 step2 보여주기
  step1.classList.add("hidden");
  step2.classList.remove("hidden");

  // 2) 10장 일렬 렌더
  renderTenCards();

  // 3) 2초 후 랜덤 5장만 앞으로(아래로) 나오게
  setTimeout(() => {
    pickedNumbers = pickFiveUnique();
    markPickedCards(pickedNumbers);
  }, 2000);
});

function renderTenCards() {
  cardRow.innerHTML = "";

  for (let n = 1; n <= 10; n++) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "card-btn dim"; // 처음엔 전부 선택 불가(흐리게)
    btn.dataset.value = String(n);

    const img = document.createElement("img");
    img.src = `${window.CARD_BASE_URL}card${n}.jpg`;
    img.alt = `card ${n}`;

    btn.appendChild(img);
    cardRow.appendChild(btn);
  }
}

// 1~10 중 5개 뽑기
function pickFiveUnique() {
  const nums = Array.from({ length: 10 }, (_, i) => i + 1);
  for (let i = nums.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [nums[i], nums[j]] = [nums[j], nums[i]];
  }
  return nums.slice(0, 5);
}

// ✅ 10장 중 뽑힌 5장만 picked로 바꾸고 클릭 가능하게
function markPickedCards(numbers) {
  const allBtns = cardRow.querySelectorAll(".card-btn");

  // 전부 dim 유지(클릭 불가)
  allBtns.forEach((btn) => {
    btn.classList.remove("picked");
    btn.classList.add("dim");
  });

  // 뽑힌 카드만 picked + 클릭 가능
  allBtns.forEach((btn) => {
    const n = Number(btn.dataset.value);
    if (numbers.includes(n)) {
      btn.classList.remove("dim");
      btn.classList.add("picked");

      btn.addEventListener("click", () => {
        showSelected(n);
      }, { once: true }); // 중복 클릭 방지
    }
  });
}

function showSelected(n) {
  // step2 숨기고 step3 표시
  step2.classList.add("hidden");
  step3.classList.remove("hidden");

  selectedImg.src = `${window.CARD_BASE_URL}card${n}.jpg`;
  selectedText.textContent = `선택한 숫자 : ${n}`;
}
