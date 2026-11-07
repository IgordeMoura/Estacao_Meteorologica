/* ==========================================================
   Dashboard Estação Meteorológica (versão Flask)
   O Python já calcula e formata tudo. Aqui o JS só faz 3 coisas:
   1) alternar o tema claro/escuro
   2) manter o relógio andando
   3) buscar /api/dados de tempos em tempos e atualizar a tela
   ========================================================== */

const INTERVALO_MS = 10000; // atualiza a cada 10 segundos

const $ = (id) => document.getElementById(id);
const root = document.documentElement;

// ---------- 1) Tema ----------
function aplicarTema(tema) {
  root.setAttribute("data-theme", tema);
  try { localStorage.setItem("tema", tema); } catch (e) {}
  const label = document.querySelector(".theme-toggle__label");
  if (label) label.textContent = tema === "dark" ? "Escuro" : "Claro";
}

function alternarTema() {
  aplicarTema(root.getAttribute("data-theme") === "dark" ? "light" : "dark");
}

// ---------- 2) Relógio ----------
function atualizarHora() {
  $("hora").textContent = new Date().toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

// ---------- 3) Atualização dos dados ----------
function atualizarTela(d) {
  $("local").textContent = d.local;
  $("temp-atual").textContent = d.temperatura;
  $("icone-temp").textContent = d.icone;
  $("desc-temp").textContent = d.descricao;

  $("pressao").textContent = d.pressao;
  $("umidade").textContent = d.umidade;
  $("luz").textContent = d.luz;

  // as duas linhas do painel da direita
  d.ultimos.forEach((linha, i) => {
    $(`ultimo-${i}-temperatura`).textContent = linha.temperatura;
    $(`ultimo-${i}-pressao`).textContent = linha.pressao;
    $(`ultimo-${i}-umidade`).textContent = linha.umidade;
  });

  // alerta: o CSS muda a cor conforme o data-status (ok / warn / danger)
  $("alerta").dataset.status = d.alerta_status;
  $("alerta-texto").textContent = d.alerta_texto;
}

async function buscarDados() {
  try {
    const resposta = await fetch("/api/dados", { cache: "no-store" });
    if (!resposta.ok) throw new Error("HTTP " + resposta.status);
    atualizarTela(await resposta.json());
  } catch (erro) {
    // se falhar, mantém o que já está na tela e avisa no console
    console.error("Não foi possível atualizar os dados:", erro);
  }
}

// ---------- Início ----------
document.addEventListener("DOMContentLoaded", () => {
  aplicarTema(root.getAttribute("data-theme") || "dark");
  $("theme-toggle").addEventListener("click", alternarTema);

  atualizarHora();
  setInterval(atualizarHora, 1000);

  setInterval(buscarDados, INTERVALO_MS);
});
