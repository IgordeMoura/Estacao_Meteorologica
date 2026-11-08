const INTERVALO = 10000;

function atualizarHora() {
  const agora = new Date();
  document.getElementById("hora").textContent = agora.toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit"
  });
}

function aplicarTema(tema) {
  const botao = document.getElementById("botao-tema");

  document.documentElement.setAttribute("data-theme", tema);

  if (tema === "dark") {
    botao.textContent = "🌙 Escuro";
  } else {
    botao.textContent = "☀️ Claro";
  }

  localStorage.setItem("tema", tema);
}

function alternarTema() {
  const temaAtual = document.documentElement.getAttribute("data-theme");

  if (temaAtual === "dark") {
    aplicarTema("light");
  } else {
    aplicarTema("dark");
  }
}

function atualizarTela(d) {
  document.getElementById("local").textContent = d.local;
  document.getElementById("temp-atual").textContent = d.temperatura;
  document.getElementById("icone-temp").textContent = d.icone;
  document.getElementById("desc-temp").textContent = d.descricao;

  document.getElementById("pressao").textContent = d.pressao;
  document.getElementById("umidade").textContent = d.umidade;
  document.getElementById("luz").textContent = d.luz;

  for (let i = 0; i < d.ultimos.length; i++) {
    document.getElementById("ultimo-" + i + "-temperatura").textContent = d.ultimos[i].temperatura;
    document.getElementById("ultimo-" + i + "-pressao").textContent = d.ultimos[i].pressao;
    document.getElementById("ultimo-" + i + "-umidade").textContent = d.ultimos[i].umidade;
  }

  document.getElementById("alerta").className = "card alerta " + d.alerta_status;
  document.getElementById("alerta-texto").textContent = d.alerta_texto;
}

function buscarDados() {
  fetch("/api/dados")
    .then(function (resposta) {
      return resposta.json();
    })
    .then(function (dados) {
      atualizarTela(dados);
    })
    .catch(function (erro) {
      console.log("Erro ao buscar os dados:", erro);
    });
}

atualizarHora();
setInterval(atualizarHora, 1000);
setInterval(buscarDados, INTERVALO);

document.getElementById("botao-tema").addEventListener("click", alternarTema);
aplicarTema(localStorage.getItem("tema") || "dark");
