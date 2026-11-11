/* 제품 목록. 홈(대표 제품)과 제품 페이지가 같이 쓴다. 담당: 정연(윤).
   지금 값은 1차 틀을 띄우려고 넣은 가짜다. 이름 규칙(T-01 등)과 가격은 윤과 어가 정해 바꾼다.
   fetch 대신 JS 파일로 둔 이유: 파일을 더블클릭해 열어도(서버 없이) 보이게 하려고.
   type: table(테이블) / stand(스탠드) / pendant(펜던트) */
window.GYEOL_PRODUCTS = [
  { code: "T-01", name: "달 테이블", type: "table", width: 25, height: 32, price: 89000, featured: true },
  { code: "T-02", name: "작은 등 테이블", type: "table", width: 18, height: 24, price: 59000 },
  { code: "T-03", name: "기둥 테이블", type: "table", width: 20, height: 45, price: 109000 },
  { code: "S-01", name: "긴 기둥 스탠드", type: "stand", width: 30, height: 120, price: 239000, featured: true },
  { code: "S-02", name: "세 겹 스탠드", type: "stand", width: 40, height: 150, price: 319000 },
  { code: "S-03", name: "낮은 스탠드", type: "stand", width: 35, height: 80, price: 189000 },
  { code: "P-01", name: "구름 펜던트", type: "pendant", width: 60, height: 45, price: 179000, featured: true },
  { code: "P-02", name: "큰 달 펜던트", type: "pendant", width: 80, height: 80, price: 259000 },
  { code: "P-03", name: "길쭉 펜던트", type: "pendant", width: 35, height: 70, price: 149000 },
];

window.GYEOL_TYPES = { table: "테이블", stand: "스탠드", pendant: "펜던트" };

/* 제품 카드 한 장의 HTML. 홈과 제품 페이지가 같은 모양을 쓰도록 여기 둔다 */
window.gyeolProductCard = function (p) {
  const won = p.price.toLocaleString("ko-KR") + "원";
  return `
    <article class="product-card">
      <div class="ph">${p.code} 사진</div>
      <p class="name">${p.code} ${p.name}</p>
      <p class="meta">${window.GYEOL_TYPES[p.type]}, 지름 ${p.width}cm 높이 ${p.height}cm</p>
      <p class="meta">${won}</p>
    </article>`;
};
