<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Beşiktaş 2024-2025 Detaylı Bilet Analizi</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <!-- Chart.js DataLabels Eklentisi -->
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.0.0"></script>
    <!-- SheetJS Kütüphanesi -->
    <script src="https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" />
    <style>
        body { font-family: 'Roboto', sans-serif; }
        .bjk-black { background-color: #000000; }
        .bjk-white { background-color: #FFFFFF; }
        .bjk-red { background-color: #E30613; }
        .bjk-gray { background-color: #F3F4F6; }
        
        /* Modal Animation */
        .modal { transition: opacity 0.25s ease; }
        body.modal-active { overflow: hidden; }

        /* Custom Scrollbar */
        .custom-scrollbar::-webkit-scrollbar {
            height: 12px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
            background: #f1f1f1; 
            border-radius: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
            background: #888; 
            border-radius: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
            background: #E30613; 
        }
    </style>
</head>
<body class="bg-gray-100 min-h-screen flex flex-col">

    <!-- Header -->
    <header class="bjk-black text-white p-6 shadow-xl z-10 sticky top-0">
        <div class="container mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
            <div class="flex items-center gap-5">
                <div class="bg-white text-black font-black rounded-full w-14 h-14 flex items-center justify-center text-2xl border-4 border-gray-300 shadow-lg">BJK</div>
                <div>
                    <h1 class="text-3xl font-black tracking-tight uppercase">Beşiktaş JK</h1>
                    <p class="text-sm text-gray-400 font-medium tracking-wide">2024-2025 Sezonu Bedelsiz Bilet Raporu</p>
                </div>
            </div>
            
            <!-- File Upload Section -->
            <div class="flex items-center gap-3 bg-gray-800 p-3 rounded-xl border border-gray-700 shadow-lg">
                <label for="fileInput" class="cursor-pointer bg-red-600 hover:bg-red-700 text-white text-sm font-bold py-2 px-5 rounded-lg transition flex items-center gap-2 shadow hover:shadow-lg transform hover:-translate-y-0.5">
                    <i class="fas fa-file-excel text-lg"></i>
                    <span>DOSYA YÜKLE</span>
                </label>
                <input type="file" id="fileInput" accept=".csv, .xlsx, .xls" class="hidden" onchange="handleFileUpload(this)">
                <span class="text-xs text-gray-400 hidden md:inline font-medium px-2">XLSX veya CSV</span>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto p-4 md:p-8 flex-grow space-y-8">
        
        <!-- Stats Overview Cards -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
            <!-- Card 1 -->
            <div class="bg-white p-6 rounded-xl shadow-lg border-l-8 border-black transform hover:scale-105 transition duration-300">
                <div class="flex justify-between items-start">
                    <div>
                        <h3 class="text-gray-400 text-xs font-bold uppercase tracking-widest mb-1">Analiz Edilen Maç</h3>
                        <p class="text-4xl font-black text-gray-800" id="totalMatches">0</p>
                    </div>
                    <div class="bg-gray-100 p-3 rounded-full">
                        <i class="fas fa-futbol text-gray-800 text-2xl"></i>
                    </div>
                </div>
            </div>
            <!-- Card 2 -->
            <div class="bg-white p-6 rounded-xl shadow-lg border-l-8 border-red-600 transform hover:scale-105 transition duration-300">
                <div class="flex justify-between items-start">
                    <div>
                        <h3 class="text-gray-400 text-xs font-bold uppercase tracking-widest mb-1">Toplam Bedelsiz Bilet</h3>
                        <p class="text-4xl font-black text-red-600" id="totalTickets">0</p>
                    </div>
                    <div class="bg-red-50 p-3 rounded-full">
                        <i class="fas fa-ticket-alt text-red-600 text-2xl"></i>
                    </div>
                </div>
            </div>
            <!-- Card 3 -->
            <div class="bg-white p-6 rounded-xl shadow-lg border-l-8 border-gray-400 transform hover:scale-105 transition duration-300">
                <div class="flex justify-between items-start">
                    <div class="overflow-hidden">
                        <h3 class="text-gray-400 text-xs font-bold uppercase tracking-widest mb-1">Rekor Maç</h3>
                        <p class="text-xl font-bold text-gray-800 truncate w-full" id="topMatch">-</p>
                        <p class="text-lg text-gray-500 font-bold mt-1" id="topMatchCount">0 Bilet</p>
                    </div>
                    <div class="bg-gray-100 p-3 rounded-full flex-shrink-0 ml-2">
                        <i class="fas fa-trophy text-yellow-500 text-2xl"></i>
                    </div>
                </div>
            </div>
        </div>

        <!-- Charts Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            <!-- Main Bar Chart Section -->
            <div class="lg:col-span-2 bg-white p-8 rounded-xl shadow-lg flex flex-col">
                <div class="flex flex-col md:flex-row justify-between items-center border-b border-gray-100 pb-6 mb-6">
                    <div>
                        <h2 class="text-2xl font-black text-gray-800 flex items-center gap-2">
                            <i class="fas fa-chart-bar text-red-600"></i> Maç Bazlı Karşılaştırma
                        </h2>
                        <p class="text-sm text-gray-500 mt-1 font-medium">Bilet yoğunluğunu görmek için sütunları inceleyin. Yatay kaydırma mevcuttur.</p>
                    </div>
                    <button onclick="downloadChart('mainChart', 'Besiktas_Bilet_Analizi_Bar')" class="mt-4 md:mt-0 bg-gray-800 hover:bg-black text-white text-xs font-bold py-2.5 px-5 rounded-lg flex items-center gap-2 transition shadow hover:shadow-md">
                        <i class="fas fa-download"></i> PNG İNDİR
                    </button>
                </div>
                
                <!-- Scrollable Container for Wide Charts -->
                <div class="overflow-x-auto custom-scrollbar pb-4 w-full">
                    <!-- Dinamik Genişlik için Wrapper -->
                    <div id="chartContainerWrapper" class="relative h-[500px] min-w-full">
                        <canvas id="mainChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Pie Chart Section -->
            <div class="lg:col-span-1 bg-white p-8 rounded-xl shadow-lg flex flex-col">
                <div class="flex justify-between items-center border-b border-gray-100 pb-6 mb-6">
                    <div>
                        <h2 class="text-xl font-black text-gray-800 flex items-center gap-2">
                            <i class="fas fa-chart-pie text-gray-600"></i> Genel Dağılım
                        </h2>
                        <p class="text-xs text-gray-500 mt-1 font-medium">Maçların toplama oranı</p>
                    </div>
                    <button onclick="downloadChart('overviewPieChart', 'Besiktas_Bilet_Analizi_Pie')" class="bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-bold py-2 px-3 rounded-lg flex items-center gap-2 transition">
                        <i class="fas fa-download"></i>
                    </button>
                </div>
                <div class="relative flex-grow flex items-center justify-center h-[400px]">
                    <canvas id="overviewPieChart"></canvas>
                </div>
            </div>

        </div>

        <!-- Data Table -->
        <div class="bg-white p-8 rounded-xl shadow-lg">
            <h2 class="text-2xl font-black mb-6 text-gray-800 border-b border-gray-100 pb-4">Detaylı Maç Listesi</h2>
            <div class="overflow-x-auto rounded-lg border border-gray-200">
                <table class="min-w-full text-left text-sm whitespace-nowrap">
                    <thead class="bg-black text-white uppercase tracking-wider font-bold">
                        <tr>
                            <th scope="col" class="px-6 py-5">#</th>
                            <th scope="col" class="px-6 py-5">Maç Adı</th>
                            <th scope="col" class="px-6 py-5 text-right">Toplam Bilet</th>
                            <th scope="col" class="px-6 py-5 text-center">İşlem</th>
                        </tr>
                    </thead>
                    <tbody id="dataTableBody" class="divide-y divide-gray-100 bg-white">
                        <!-- Rows via JS -->
                    </tbody>
                </table>
            </div>
        </div>
    </main>

    <footer class="text-center p-8 text-gray-500 text-sm bg-white border-t mt-8 font-medium">
        <p>Beşiktaş Jimnastik Kulübü Raporlama Aracı &copy; 2025</p>
        <p class="text-xs text-gray-400 mt-1">Gelişmiş Veri Analiz Sistemi</p>
    </footer>

    <!-- MODAL FOR DRILL DOWN -->
    <div id="detailModal" class="modal opacity-0 pointer-events-none fixed inset-0 flex items-center justify-center z-50 px-4">
        <div class="modal-overlay absolute inset-0 bg-gray-900 opacity-75 backdrop-blur-sm"></div>
        
        <div class="modal-container bg-white w-full md:max-w-5xl mx-auto rounded-2xl shadow-2xl z-50 overflow-hidden transform transition-all scale-95" id="modalContent">
            
            <!-- Modal Header -->
            <div class="modal-header flex justify-between items-center p-6 bg-gray-50 border-b border-gray-100">
                <div>
                    <h2 class="text-2xl font-black text-gray-900" id="modalTitle">Maç Detayı</h2>
                    <p class="text-sm text-gray-500 font-bold mt-1">Tribün Bazlı Dağılım Raporu</p>
                </div>
                <div class="flex items-center gap-3">
                    <button onclick="downloadChart('detailChart', 'Tribun_Detayi')" class="bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 text-xs font-bold py-2 px-4 rounded-lg transition shadow-sm flex items-center gap-2">
                        <i class="fas fa-download"></i> Grafik
                    </button>
                    <button onclick="closeModal()" class="text-gray-400 hover:text-red-600 transition p-2">
                        <i class="fas fa-times text-2xl"></i>
                    </button>
                </div>
            </div>

            <!-- Modal Body -->
            <div class="modal-content p-8 bg-white overflow-y-auto max-h-[70vh]">
                <div class="flex flex-col lg:flex-row gap-10">
                    <!-- Chart Side -->
                    <div class="w-full lg:w-1/2 flex flex-col items-center justify-center bg-gray-50 rounded-xl p-6 border border-gray-100">
                         <h4 class="font-bold text-gray-800 mb-6 text-lg">Görsel Dağılım</h4>
                         <div class="relative h-80 w-full">
                            <canvas id="detailChart"></canvas>
                         </div>
                    </div>
                    
                    <!-- List Side -->
                    <div class="w-full lg:w-1/2">
                        <h4 class="font-bold text-gray-800 mb-4 text-lg border-b pb-2 flex justify-between">
                            <span>Tribün Listesi</span>
                            <span class="text-xs bg-gray-200 text-gray-600 px-2 py-1 rounded">Sıralı Liste</span>
                        </h4>
                        <div class="overflow-y-auto max-h-80 pr-2 custom-scrollbar">
                            <table class="w-full text-sm">
                                <thead class="text-xs text-gray-500 bg-gray-50 uppercase sticky top-0">
                                    <tr>
                                        <th class="py-3 px-2 text-left rounded-l-md">Tribün Adı</th>
                                        <th class="py-3 px-2 text-right rounded-r-md">Adet</th>
                                    </tr>
                                </thead>
                                <tbody id="modalTableBody" class="divide-y divide-gray-100">
                                    <!-- Dynamic Content -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Modal Footer -->
            <div class="modal-footer p-4 bg-gray-50 border-t border-gray-100 text-right">
                <button onclick="closeModal()" class="bg-black hover:bg-gray-800 text-white font-bold py-3 px-8 rounded-lg shadow-lg transition transform hover:scale-105">
                    KAPAT
                </button>
            </div>
        </div>
    </div>

    <script>
        // Chart.js Default Font Settings (Global Larger Fonts)
        Chart.defaults.font.family = "'Roboto', sans-serif";
        Chart.defaults.font.size = 13;
        Chart.defaults.color = '#4B5563';
        
        Chart.register(ChartDataLabels);

        // --- 1. DEFAULT DEMO DATA ---
        let rawCsvData = `Maç,Tribün,Bilet Sayısı
Beşiktaş United Payment - Galatasaray A.Ş.,BATI NUMARALI LOCA,801
Beşiktaş United Payment - Galatasaray A.Ş.,DOĞU ALT TRİBÜNÜ,11
Beşiktaş United Payment - Galatasaray A.Ş.,DOĞU KAPALI LOCA,749
Beşiktaş United Payment - Galatasaray A.Ş.,ENGELLİ TRİBÜNÜ,100
Beşiktaş United Payment - Galatasaray A.Ş.,GÜNEY LOCA,1272
Beşiktaş United Payment - Galatasaray A.Ş.,VIP TRİBÜNÜ,398
Beşiktaş A.Ş. Taraftara Açık Antrenman,DOĞU ALT TRİBÜNÜ,4588
Beşiktaş A.Ş. Kasımpaşa A.Ş.,BATI ALT TRİBÜNÜ,132
Beşiktaş A.Ş. Kasımpaşa A.Ş.,BATI NUMARALI LOCA,42
Beşiktaş A.Ş. Kasımpaşa A.Ş.,BATI ÜST TRİBÜNÜ,11
Beşiktaş A.Ş. Kasımpaşa A.Ş.,DOĞU ALT TRİBÜNÜ,207
Beşiktaş A.Ş. Kasımpaşa A.Ş.,DOĞU KAPALI LOCA,14
Beşiktaş A.Ş. Kasımpaşa A.Ş.,DOĞU ÜST TRİBÜNÜ,97
Beşiktaş A.Ş. Kasımpaşa A.Ş.,GÜNEY ALT TRİBÜNÜ,9
Beşiktaş - Lugano,BATI ÜST TRİBÜNÜ,15
Beşiktaş - Lugano,DOĞU ALT TRİBÜNÜ,267
Beşiktaş - Lugano,DOĞU KAPALI LOCA,40
Beşiktaş - Lugano,DOĞU ÜST TRİBÜNÜ,4
Beşiktaş - Lugano,GÜNEY ALT TRİBÜNÜ,5
Beşiktaş - Lugano,GÜNEY ÜST TRİBÜNÜ,22
Beşiktaş - Lugano,KUZEY ALT TRİBÜNÜ,21
Beşiktaş - Lugano,GÜNEY LOCA,48
Beşiktaş - Lugano,KUZEY ÜST TRİBÜNÜ,44
Beşiktaş - Lugano,VIP TRİBÜNÜ,323
Beşiktaş - Frankfurt,BATI ALT TRİBÜNÜ,212
Beşiktaş - Frankfurt,BATI NUMARALI LOCA,69
Beşiktaş - Frankfurt,BATI ÜST TRİBÜNÜ,3
Beşiktaş - Frankfurt,DOĞU ALT TRİBÜNÜ,381
Beşiktaş - Frankfurt,DOĞU KAPALI LOCA,44
Beşiktaş - Frankfurt,DOĞU ÜST TRİBÜNÜ,13
Beşiktaş - Frankfurt,GÜNEY ALT TRİBÜNÜ,11
Beşiktaş - Frankfurt,GÜNEY ÜST TRİBÜNÜ,18
Beşiktaş - Frankfurt,KUZEY ALT TRİBÜNÜ,30
Beşiktaş - Frankfurt,GÜNEY LOCA,34
Beşiktaş - Frankfurt,KUZEY ÜST TRİBÜNÜ,15`;

        let globalMatchData = {}; 
        let mainChartInstance = null;
        let pieChartInstance = null;
        let detailChartInstance = null;

        // --- 2. DOWNLOAD CHART ---
        function downloadChart(chartId, fileName) {
            const canvas = document.getElementById(chartId);
            if(!canvas) return;
            const link = document.createElement('a');
            link.download = fileName + '_' + new Date().toISOString().slice(0,10) + '.png';
            // Arka planı beyaz yapmak için
            const ctx = canvas.getContext('2d');
            ctx.save();
            ctx.globalCompositeOperation = 'destination-over';
            ctx.fillStyle = 'white';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.restore();
            
            link.href = canvas.toDataURL('image/png', 1.0);
            link.click();
        }

        // --- 3. FILE UPLOAD ---
        function handleFileUpload(input) {
            const file = input.files[0];
            if (!file) return;

            const fileName = file.name.toLowerCase();
            const reader = new FileReader();

            if (fileName.endsWith('.xlsx') || fileName.endsWith('.xls')) {
                reader.onload = function(e) {
                    const data = new Uint8Array(e.target.result);
                    try {
                        const workbook = XLSX.read(data, {type: 'array'});
                        const firstSheetName = workbook.SheetNames[0];
                        const worksheet = workbook.Sheets[firstSheetName];
                        const csvOutput = XLSX.utils.sheet_to_csv(worksheet);
                        initDashboard(csvOutput);
                        alert("Veriler başarıyla analiz edildi.");
                    } catch (error) {
                        console.error(error);
                        alert("Dosya formatı hatası.");
                    }
                };
                reader.readAsArrayBuffer(file);
            } else {
                reader.onload = function(e) {
                    initDashboard(e.target.result);
                    alert("Veriler başarıyla analiz edildi.");
                };
                reader.readAsText(file);
            }
        }

        // --- 4. PROCESS DATA ---
        function processData(csvText) {
            const lines = csvText.trim().split('\n');
            const matches = {};
            let grandTotal = 0;

            // Header Detection Logic: Find the row that contains "Maç" or "Tribün"
            let startIndex = 0;
            for(let i=0; i<lines.length; i++) {
                const lowerLine = lines[i].toLowerCase();
                if(lowerLine.includes("maç") || lowerLine.includes("tribün") || lowerLine.includes("tribun")) {
                    startIndex = i + 1; // Start processing from the next line
                    break;
                }
            }

            for (let i = startIndex; i < lines.length; i++) {
                const line = lines[i];
                if (!line || line.trim() === "") continue;

                const parts = line.split(',');
                if(parts.length < 3) continue;

                let countStr = parts[parts.length - 1].trim().replace(/['"]+/g, '');
                const count = parseInt(countStr);
                
                if (isNaN(count)) continue;

                let tribune = parts[parts.length - 2].trim().replace(/^"|"$/g, '');
                let matchName = parts.slice(0, parts.length - 2).join(',').trim()
                                     .replace(/^"|"$/g, '').replace(/""/g, '');

                if (matchName.toLowerCase().includes("total") || matchName.toLowerCase().includes("toplam")) continue;

                if (!matches[matchName]) {
                    matches[matchName] = {
                        total: 0,
                        tribunes: {}
                    };
                }

                matches[matchName].total += count;
                grandTotal += count;

                if (!matches[matchName].tribunes[tribune]) {
                    matches[matchName].tribunes[tribune] = 0;
                }
                matches[matchName].tribunes[tribune] += count;
            }
            return { matches, grandTotal };
        }

        // --- COLOR GENERATOR ---
        // Veri büyüklüğüne göre kırmızı tonları üretir (Koyu Kırmızı -> Siyah)
        function generateColorGradient(values) {
            const maxVal = Math.max(...values);
            return values.map(val => {
                // Opaklık değil, renk tonu değişimi
                // Değer yüksekse daha canlı kırmızı (#E30613), düşükse daha gri/siyah
                const ratio = val / maxVal;
                if (ratio > 0.8) return '#E30613'; // Beşiktaş Red
                if (ratio > 0.5) return '#991B1B'; // Dark Red
                if (ratio > 0.2) return '#374151'; // Dark Gray
                return '#9CA3AF'; // Light Gray
            });
        }

        // --- 5. INIT DASHBOARD ---
        function initDashboard(csvData = rawCsvData) {
            const { matches, grandTotal } = processData(csvData);
            globalMatchData = matches;

            const sortedMatchesArr = Object.entries(matches)
                .sort((a, b) => b[1].total - a[1].total);

            const labels = sortedMatchesArr.map(item => item[0]);
            const dataValues = sortedMatchesArr.map(item => item[1].total);

            // KPI Update
            document.getElementById('totalMatches').innerText = labels.length;
            document.getElementById('totalTickets').innerText = grandTotal.toLocaleString('tr-TR');
            if(sortedMatchesArr.length > 0) {
                document.getElementById('topMatch').innerText = sortedMatchesArr[0][0];
                document.getElementById('topMatchCount').innerText = sortedMatchesArr[0][1].total.toLocaleString('tr-TR') + " Bilet";
            } else {
                 document.getElementById('topMatch').innerText = "-";
                 document.getElementById('topMatchCount').innerText = "0 Bilet";
            }

            // Table Update
            const tableBody = document.getElementById('dataTableBody');
            tableBody.innerHTML = '';
            sortedMatchesArr.forEach(([matchName, data], index) => {
                const row = document.createElement('tr');
                row.className = "hover:bg-red-50 transition border-b border-gray-100 group";
                const safeMatchName = matchName.replace(/'/g, "\\'");
                // Yüksek biletli satırları vurgula
                const intensityClass = index < 3 ? "font-black text-gray-900" : "text-gray-700";
                
                row.innerHTML = `
                    <td class="px-6 py-4 text-gray-400 font-medium group-hover:text-red-600">${index + 1}</td>
                    <td class="px-6 py-4 font-medium ${intensityClass}">${matchName}</td>
                    <td class="px-6 py-4 text-right font-bold ${index === 0 ? 'text-red-600' : 'text-gray-800'}">${data.total.toLocaleString('tr-TR')}</td>
                    <td class="px-6 py-4 text-center">
                        <button onclick="openModal('${safeMatchName}')" class="bg-white border border-gray-300 text-gray-600 hover:bg-black hover:text-white hover:border-black px-4 py-1.5 rounded-full text-xs font-bold transition shadow-sm">
                            İNCELE
                        </button>
                    </td>
                `;
                tableBody.appendChild(row);
            });

            // 1. MAIN CHART (BAR)
            const chartWrapper = document.getElementById('chartContainerWrapper');
            // Veri sayısına göre genişlik ayarla (En az %100, her bar için 60px)
            // Bu sayede yatay scroll oluşur
            const minWidth = Math.max(100, labels.length * 60); 
            // Eğer mobildeysek daha da dar olabilir ama masaüstünde geniş olsun
            chartWrapper.style.width = labels.length > 10 ? `${minWidth}px` : '100%';

            const ctxMain = document.getElementById('mainChart').getContext('2d');
            if (mainChartInstance) mainChartInstance.destroy();

            // Renkleri oluştur
            const barColors = generateColorGradient(dataValues);

            mainChartInstance = new Chart(ctxMain, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Bedelsiz Bilet',
                        data: dataValues,
                        backgroundColor: barColors,
                        borderRadius: 6,
                        barPercentage: 0.7, // Sütun kalınlığı
                        categoryPercentage: 0.8
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    layout: {
                        padding: { top: 30, bottom: 10, left: 10, right: 10 }
                    },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            backgroundColor: 'rgba(0,0,0,0.9)',
                            titleFont: { size: 14 },
                            bodyFont: { size: 14 },
                            padding: 12,
                            callbacks: {
                                label: (c) => ` ${c.raw.toLocaleString('tr-TR')} Adet`
                            }
                        },
                        datalabels: {
                            anchor: 'end',
                            align: 'top',
                            formatter: (val) => val.toLocaleString('tr-TR'),
                            font: { weight: 'bold', size: 12 },
                            color: '#374151',
                            offset: 4
                        }
                    },
                    onClick: (e) => {
                        const activePoints = mainChartInstance.getElementsAtEventForMode(e, 'nearest', { intersect: true }, true);
                        if (activePoints.length) {
                            openModal(mainChartInstance.data.labels[activePoints[0].index]);
                        }
                    },
                    scales: {
                        y: { 
                            beginAtZero: true, 
                            grid: { color: '#f3f4f6' },
                            ticks: { font: { size: 12 } }
                        },
                        x: { 
                            grid: { display: false }, 
                            ticks: { 
                                font: { size: 11, weight: '500' },
                                maxRotation: 45,
                                minRotation: 45
                            } 
                        }
                    }
                }
            });

            // 2. PIE CHART
            const ctxPie = document.getElementById('overviewPieChart').getContext('2d');
            if (pieChartInstance) pieChartInstance.destroy();

            pieChartInstance = new Chart(ctxPie, {
                type: 'doughnut', // Pie yerine Doughnut daha şık
                data: {
                    labels: labels,
                    datasets: [{
                        data: dataValues,
                        backgroundColor: [
                            '#E30613', '#111827', '#374151', '#4B5563', '#6B7280', 
                            '#9CA3AF', '#D1D5DB', '#FCA5A5', '#F87171', '#EF4444'
                        ],
                        borderWidth: 2,
                        borderColor: '#ffffff',
                        hoverOffset: 10
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '50%', // Ortası boşluk
                    plugins: {
                        legend: {
                            display: true,
                            position: 'bottom',
                            labels: {
                                usePointStyle: true,
                                padding: 20,
                                font: { size: 11 }
                            }
                        },
                        datalabels: {
                            display: function(context) {
                                // Sadece %4'ten büyük dilimlere yazı yaz
                                let dataset = context.chart.data.datasets[0];
                                let total = dataset.data.reduce((acc, val) => acc + val, 0);
                                let value = dataset.data[context.dataIndex];
                                return (value / total * 100) > 4;
                            },
                            color: '#fff',
                            font: { weight: 'bold', size: 12 },
                            formatter: (value, ctx) => {
                                let sum = 0;
                                let dataArr = ctx.chart.data.datasets[0].data;
                                dataArr.map(data => { sum += data; });
                                return (value * 100 / sum).toFixed(0) + "%";
                            }
                        }
                    }
                }
            });
        }

        // --- 6. MODAL ---
        function openModal(matchName) {
            const modal = document.getElementById('detailModal');
            const title = document.getElementById('modalTitle');
            const tableBody = document.getElementById('modalTableBody');
            const modalContent = document.getElementById('modalContent');
            const body = document.querySelector('body');

            title.innerText = matchName;
            
            const matchData = globalMatchData[matchName];
            if (!matchData) return;

            const sortedTribunes = Object.entries(matchData.tribunes)
                .sort((a, b) => b[1] - a[1]);

            tableBody.innerHTML = '';
            sortedTribunes.forEach(([tribuneName, count]) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="py-3 px-2 text-gray-700 font-medium border-b border-gray-50">${tribuneName}</td>
                    <td class="py-3 px-2 text-right font-bold text-gray-900 border-b border-gray-50">${count.toLocaleString('tr-TR')}</td>
                `;
                tableBody.appendChild(tr);
            });

            if (detailChartInstance) detailChartInstance.destroy();

            const ctx = document.getElementById('detailChart').getContext('2d');
            
            detailChartInstance = new Chart(ctx, {
                type: 'bar', // Detayda Bar chart daha okunaklı olabilir (Tribün isimleri uzun)
                indexAxis: 'y', // Yatay bar chart
                data: {
                    labels: sortedTribunes.map(t => t[0]),
                    datasets: [{
                        label: 'Bilet Adedi',
                        data: sortedTribunes.map(t => t[1]),
                        backgroundColor: '#E30613',
                        borderRadius: 4,
                        barThickness: 20
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y',
                    plugins: {
                        legend: { display: false },
                        datalabels: {
                            anchor: 'end',
                            align: 'end',
                            formatter: (val) => val.toLocaleString('tr-TR'),
                            font: { weight: 'bold', size: 10 },
                            color: '#374151'
                        }
                    },
                    scales: {
                        x: { beginAtZero: true, grid: { color: '#f3f4f6' } },
                        y: { 
                            grid: { display: false },
                            ticks: { font: { size: 10 } }
                        }
                    }
                }
            });

            modal.classList.remove('opacity-0', 'pointer-events-none');
            modalContent.classList.remove('scale-95');
            modalContent.classList.add('scale-100');
            body.classList.add('modal-active');
        }

        function closeModal() {
            const modal = document.getElementById('detailModal');
            const modalContent = document.getElementById('modalContent');
            const body = document.querySelector('body');
            
            modal.classList.add('opacity-0', 'pointer-events-none');
            modalContent.classList.remove('scale-100');
            modalContent.classList.add('scale-95');
            body.classList.remove('modal-active');
        }

        document.querySelector('.modal-overlay').addEventListener('click', closeModal);
        document.onkeydown = function(evt) {
            if (evt.keyCode == 27) closeModal();
        };

        window.onload = () => initDashboard();

    </script>
</body>
</html>