/* 온도(ONDO) 공통 머리 메뉴와 바닥. 모든 페이지가 같은 것을 쓰도록 여기 한 곳에서 그린다.
   페이지에 <header data-site-header></header>, <footer data-site-footer></footer> 를 두고 이 파일을 불러오면 채워진다.
   메뉴를 바꾸려면 PAGES만 고친다. 경로는 이 파일 위치 기준이라 어느 페이지에서 불러도 맞는다. */
(function () {
  const PAGES = [
    { key: "home", label: "홈", path: "pages/home/" },
    { key: "product", label: "제품", path: "pages/product/" },
    { key: "story", label: "스토리", path: "pages/story/" },
    { key: "magazine", label: "매거진", path: "pages/magazine/" },
    { key: "faq", label: "FAQ", path: "pages/faq/" },
  ];
  // 이 스크립트 주소에서 사이트 맨 위 주소를 구한다 (…/common/layout.js → …/)
  const root = new URL("../", document.currentScript.src);
  const current = document.body.dataset.page; // <body data-page="faq"> 처럼 각 페이지가 적는다

  const links = PAGES.map((p) =>
    `<a href="${new URL(p.path, root)}"${p.key === current ? ' aria-current="page"' : ""}>${p.label}</a>`
  ).join("");

  const header = document.querySelector("[data-site-header]");
  if (header) {
    header.className = "site-header";
    header.innerHTML = `
      <div class="wrap">
        <a class="logo" href="${new URL("pages/home/", root)}">ONDO</a>
        <button class="menu-button" type="button" aria-expanded="false" aria-controls="site-nav">메뉴</button>
        <nav class="nav" id="site-nav" aria-label="주 메뉴">${links}</nav>
      </div>`;
    const button = header.querySelector(".menu-button");
    const nav = header.querySelector(".nav");
    button.addEventListener("click", () => {
      const open = nav.classList.toggle("open");
      button.setAttribute("aria-expanded", String(open));
    });
  }

  const footer = document.querySelector("[data-site-footer]");
  if (footer) {
    footer.className = "site-footer";
    footer.innerHTML = `
      <div class="wrap">
        <div>
          <p class="logo">ONDO</p>
          <p>대나무 살과 한지로 만드는 빛</p>
          <p>수업 과제로 만든 가상 브랜드예요. 실제로 판매하지 않아요.</p>
        </div>
        <nav class="footer-nav" aria-label="바닥 메뉴">${links}</nav>
      </div>`;
  }
})();
