// Configuração da API
const API_BASE_URL = 'http://localhost:8000/api';

// Registrar o plugin de datalabels
Chart.register(ChartDataLabels);

// Variáveis globais
let dadosProducao = [];
let chart = null;
let map = null;

// Função para formatar números
function formatarNumero(numero) {
    if (numero === '-' || numero === null || numero === undefined) {
        return '0';
    }
    return parseInt(numero).toLocaleString('pt-BR');
}

// Função para buscar dados da API
async function buscarDados(ano = null, cultura = null) {
    try {
        showLoading();
        
        // Construir URL da API com base nos filtros
        let url = `${API_BASE_URL}/data/`;
        const params = new URLSearchParams();
        if (ano) {
            params.append("ano", ano);
        }
        if (cultura) {
            params.append("cultura", cultura);
        }
       
        if (params.toString()) {
            url += `?${params.toString()}`;
        }
        
        // Buscar dados de produção
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Erro na API: ${response.status}`);
        }
        
        const data = await response.json();
        dadosProducao = data.dados || [];
        
        // Processar e exibir os dados
        processarDados();
        criarGrafico();
        criarMapa();
        
        hideLoading();
        
    } catch (error) {
        console.error('Erro ao buscar dados:', error);
        hideLoading();
        
        // Usar dados de exemplo em caso de erro
        usarDadosExemplo();
    }
}

// Função para usar dados de exemplo (fallback)
function usarDadosExemplo() {
    console.log('Usando dados de exemplo...');
    
    // Dados de exemplo baseados nos arquivos fornecidos
    dadosProducao = [
        { D1N: "Sudoeste Piauiense - PI", V: "2994156" },
        { D1N: "Sul Maranhense - MA", V: "2232684" },
        { D1N: "Ocidental do Tocantins - TO", V: "2059044" },
        { D1N: "Sudeste Paraense - PA", V: "1988378" },
        { D1N: "Oriental do Tocantins - TO", V: "1726342" },
        { D1N: "Leste Rondoniense - RO", V: "1429058" },
        { D1N: "Oeste Maranhense - MA", V: "613242" },
        { D1N: "Leste Maranhense - MA", V: "538388" },
        { D1N: "Baixo Amazonas - PA", V: "387808" },
        { D1N: "Norte de Roraima - RR", V: "320335" }
    ];
    
    processarDados();
    criarGrafico();
    criarMapa();
}

// Função para processar os dados
function processarDados() {
    // Filtrar dados válidos e ordenar por produção
    const dadosValidos = dadosProducao
        .filter(item => item.V && item.V !== '-' && parseInt(item.V) > 0)
        .sort((a, b) => parseInt(b.V) - parseInt(a.V));
    
    // Calcular estatísticas
    const totalProducao = dadosValidos.reduce((total, item) => total + parseInt(item.V), 0);
    const totalRegioes = dadosValidos.length;
    const maiorProdutor = dadosValidos[0];
    
    // Atualizar elementos da página
    document.getElementById('total-producao').textContent = formatarNumero(totalProducao);
    document.getElementById('total-regioes').textContent = totalRegioes;
    document.getElementById('maior-produtor').textContent = maiorProdutor ? maiorProdutor.D1N : 'N/A';
}

// Função para criar o gráfico
function criarGrafico() {
    const ctx = document.getElementById('producaoChart').getContext('2d');
    
    // Pegar os top 10 produtores
    const dadosValidos = dadosProducao
        .filter(item => item.V && item.V !== '-' && parseInt(item.V) > 0)
        .sort((a, b) => parseInt(b.V) - parseInt(a.V))
        .slice(0, 10);
    
    const labels = dadosValidos.map(item => item.D1N.split(' - ')[0]);
    const dados = dadosValidos.map(item => parseInt(item.V));
    
    // Destruir gráfico anterior se existir
    if (chart) {
        chart.destroy();
    }
    
    chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Produção (Toneladas)',
                data: dados,
                backgroundColor: [
                '#CC4400', '#E55100', '#FF5722', '#FF6633', '#FF7744',
                '#FF8855', '#FF9966', '#CD7F32', '#D2691E', '#DEB887'
            ],
            borderColor: [
                '#27252496', 
            ],
            borderWidth: 2,
            borderRadius: 6,
            borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Top 10 Regiões Produtoras',
                    font: {
                        size: 16,
                        weight: 'bold'
                    },
                    color: '#e26838ff'
                },
                legend: {
                    display: false
                },
                datalabels: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${formatarNumero(context.parsed.y)} toneladas`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatarNumero(value);
                        }
                    },
                    grid: {
                        color: '#e6eaeeff'
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    },
                    grid: {
                        display: false
                    }
                }
            },
            animation: {
                duration: 1500,
                easing: 'easeOutQuart'
            }
        }
    });
}

// Cache para coordenadas
let coordenadasCache = {};

// Função para buscar coordenadas usando geocodificação
async function buscarCoordenadas(nomeRegiao) {
    // Verificar cache
    if (coordenadasCache[nomeRegiao]) {
        return coordenadasCache[nomeRegiao];
    }

    try {
        // Tratativa de nome das regioes
        let termoBusca = nomeRegiao;
        if (nomeRegiao.includes(' - ')) {
            const partes = nomeRegiao.split(' - ');
            const regiao = partes[0];
            const uf = partes[1];
            termoBusca = `${regiao}, ${uf}, Brasil`;
        } else {
            termoBusca = `${nomeRegiao}, Brasil`;
        }

        // Busca na API o localização
        const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(termoBusca)}&limit=1&countrycodes=br`;
        
        const response = await fetch(url);
        const data = await response.json();

        if (data && data.length > 0) {
            const coordenadas = [parseFloat(data[0].lat), parseFloat(data[0].lon)];
            
            // Salvar no cache
            coordenadasCache[nomeRegiao] = coordenadas;
            return coordenadas;
        } else {
            return null;
        }
    } catch (error) {
        return null;
    }
}

// Função para criar o mapa com busca automática de coordenadas
async function criarMapa() {
    
    // Inicializar o mapa centrado no Brasil
    if (map) {
        map.remove();
    }
    
    map = L.map('map').setView([-15.0, -50.0], 4);
    
    // Adicionar mapa
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { 
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Filtrar e pegar apenas os TOP 10 dados válidos
    const dadosValidos = dadosProducao
        .filter(item => {
            const valido = item.V && item.V !== '-' && parseInt(item.V) > 0;
            return valido;
        })
        .sort((a, b) => parseInt(b.V) - parseInt(a.V))
        .slice(0, 10); // TOP 10
    let marcadoresAdicionados = 0;
    const maxProducao = parseInt(dadosValidos[0]?.V || 1);
    
    // Processar cada região de forma assíncrona
    for (let index = 0; index < dadosValidos.length; index++) {
        const item = dadosValidos[index];
        const nomeRegiao = item.D1N || item.regiao || item.nome;
        
        
        // Buscar coordenadas para esta região
        const coordenadas = await buscarCoordenadas(nomeRegiao);
        
        if (coordenadas) {
            const producao = parseInt(item.V);
            
            // Calcular o tamanho do marcador baseado na produção
            const tamanho = Math.max(15, (producao / maxProducao) * 40);
            
            // Definir cor ranking (TOP 10)
            let cor = '#DDEACB';
            if (index === 0) cor = '#FF6B35';
            else if (index <= 2) cor = '#F39200';
            else if (index <= 4) cor = '#FFB84C'; 
            else if (index <= 6) cor = '#A3C586'; 
            else cor = '#DDEACB'; 
            
            // Criar marcador circular
            const marker = L.circleMarker(coordenadas, {
                radius: tamanho / 2,
                fillColor: cor,
                color: '#ffffff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            }).addTo(map);
            
            // Adicionar popup com informações detalhadas
            marker.bindPopup(`
                <div style="text-align: center; min-width: 200px;">
                    <h4 style="margin: 0 0 10px 0; color: #007A33; font-size: 14px;">
                        ${nomeRegiao}
                    </h4>
                    <div style="margin: 8px 0;">
                        <span style="background: ${cor}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold;">
                            #${index + 1} no ranking
                        </span>
                    </div>
                    <p style="margin: 10px 0 5px 0; font-size: 18px; font-weight: bold; color: #F39200;">
                        ${formatarNumero(producao)} toneladas
                    </p>
                    <p style="margin: 0; font-size: 12px; color: #666;">
                        ${((producao / dadosValidos.reduce((sum, d) => sum + parseInt(d.V), 0)) * 100).toFixed(1)}% do total
                    </p>
                </div>
            `);
            
            // Adicionar efeito hover
            marker.on('mouseover', function() {
                this.setStyle({
                    weight: 4,
                    fillOpacity: 1,
                    radius: (tamanho / 2) + 2
                });
            });
            
            marker.on('mouseout', function() {
                this.setStyle({
                    weight: 2,
                    fillOpacity: 0.8,
                    radius: tamanho / 2
                });
            });
            
            marcadoresAdicionados++;
        }
        
    }
    
    
    // Adicionar legenda 
    const legend = L.control({position: 'bottomright'});
    legend.onAdd = function() {
        const div = L.DomUtil.create('div', 'legend');
        div.style.backgroundColor = 'white';
        div.style.padding = '12px';
        div.style.borderRadius = '8px';
        div.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
        div.style.fontSize = '12px';
        
        div.innerHTML = `
            <h4 style="margin: 0 0 10px 0; color: #007A33; font-size: 14px;">TOP 10 Produtores</h4>
            <div style="display: flex; align-items: center; margin: 6px 0;">
                <div style="width: 18px; height: 18px; background: #FF6B35; border-radius: 50%; margin-right: 8px; border: 2px solid white;"></div>
                <span>1º lugar</span>
            </div>
            <div style="display: flex; align-items: center; margin: 6px 0;">
                <div style="width: 16px; height: 16px; background: #F39200; border-radius: 50%; margin-right: 8px; border: 2px solid white;"></div>
                <span>2º - 3º lugar</span>
            </div>
            <div style="display: flex; align-items: center; margin: 6px 0;">
                <div style="width: 14px; height: 14px; background: #FFB84C; border-radius: 50%; margin-right: 8px; border: 2px solid white;"></div>
                <span>4º - 5º lugar</span>
            </div>
            <div style="display: flex; align-items: center; margin: 6px 0;">
                <div style="width: 12px; height: 12px; background: #A3C586; border-radius: 50%; margin-right: 8px; border: 2px solid white;"></div>
                <span>6º - 7º lugar</span>
            </div>
            <div style="display: flex; align-items: center; margin: 6px 0;">
                <div style="width: 10px; height: 10px; background: #DDEACB; border-radius: 50%; margin-right: 8px; border: 2px solid white;"></div>
                <span>8º - 10º lugar</span>
            </div>
        `;
        
        return div;
    };
    legend.addTo(map);
    
    // Se conseguiu adicionar pelo menos um marcador, ajustar visualização
    if (marcadoresAdicionados > 0) {
        setTimeout(() => {
            try {
                const group = new L.featureGroup(map._layers);
                if (Object.keys(group._layers).length > 0) {
                    map.fitBounds(group.getBounds().pad(0.1));
                }
            } catch (error) {
            }
        }, 1000);
    }
}



// Funções de loading
function showLoading() {
    document.getElementById('total-producao').textContent = 'Carregando...';
    document.getElementById('total-regioes').textContent = 'Carregando...';
    document.getElementById('maior-produtor').textContent = 'Carregando...';
}

function hideLoading() {
    // Loading será removido quando os dados forem processados
}

// Função para testar conectividade com a API
async function testarAPI() {
    try {
        const response = await fetch(`${API_BASE_URL}/health_check`);
        if (response.ok) {
            console.log('API conectada com sucesso!');
            return true;
        }
    } catch (error) {
        console.log('Erro ao conectar com a API:', error.message);
        return false;
    }
    return false;
}

// Função para popular os selects de filtro
async function popularFiltros() {
    const anoSelect = document.getElementById("ano-select");
    const culturaSelect = document.getElementById("cultura-select");
    
    // Gera de 2024 até 2021 
    const currentYear = new Date().getFullYear();
    for (let i = 0; i < 5; i++) {
        const year = (currentYear === 2025 ? currentYear - 1 : culturaSelect) - i;
        const option = document.createElement("option");
        option.value = year;
        option.textContent = year;
        anoSelect.appendChild(option);
    }
    anoSelect.value = (currentYear === 2025 ? currentYear - 1 : currentYear);

    // Preencher culturas (buscando da API)
    try {
        const responseCulturas = await fetch(`${API_BASE_URL}/opcoes/cultures/`);
        if (responseCulturas.ok) {
            const data = await responseCulturas.json();
            const culturas = data.culturas;
            for (const id in culturas) {
                const option = document.createElement("option");
                option.value = id;
                option.textContent = culturas[id];
                culturaSelect.appendChild(option);
            }
        } else {
            console.warn("Não foi possível carregar opções de culturas da API. Usando padrão.");
            const option = document.createElement("option");
            option.value = "2713";
            option.textContent = "Soja (em grão)";
            culturaSelect.appendChild(option);
            culturaSelect.value = "2713";
        }


    } catch (error) {
        console.error("Erro ao buscar opções de culturas:", error);
        const option = document.createElement("option");
        option.value = "2713";
        option.textContent = "Soja (em grão)";
        culturaSelect.appendChild(option);
        culturaSelect.value = "2713";
    }
    
}

// Função para aplicar os filtros
async function aplicarFiltros() {
    const ano = document.getElementById("ano-select").value;
    const cultura = document.getElementById("cultura-select").value;
    console.log(`Aplicando filtros: Ano=${ano}, Cultura=${cultura}`);
    await buscarDados(ano, cultura);
}

// Inicialização quando a página carrega
document.addEventListener("DOMContentLoaded", async function() {  
    await popularFiltros();

    // Testar conectividade
    const apiConectada = await testarAPI();
    
    if (apiConectada) {
        console.log("Buscando dados da API...");
        await aplicarFiltros(); // Chama buscarDados com os filtros iniciais
    } else {
        console.log("API não disponível, usando dados de exemplo...");
        usarDadosExemplo();
    }
    
    // Adicionar evento ao botão de aplicar filtros
    document.getElementById("aplicar-filtros").addEventListener("click", aplicarFiltros);

});
