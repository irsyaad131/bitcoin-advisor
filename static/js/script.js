$(document).ready(function() {
    $('#analyze-btn').click(function() {
        const period = $('#period-select').val();
        
        // Tampilkan loading state
        $(this).html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Memproses...');
        
        $.ajax({
            url: '/get_recommendations',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ period: period }),
            success: function(response) {
                if (response.status === 'success') {
                    // Update price info
                    $('#price-info').html(`
                        <h3 class="text-warning">$${response.current_price.toLocaleString()}</h3>
                        <p class="mb-0">Per ${response.last_updated}</p>
                    `);
                    
                    // Update recommendations
                    if (response.recommendations.length > 0) {
                        let recHtml = '';
                        response.recommendations.forEach(rec => {
                            recHtml += `
                                <div class="alert alert-${getAlertClass(rec.type)} mb-2">
                                    <h6><i class="${getIconClass(rec.type)} me-2"></i>${rec.type}</h6>
                                    <p class="mb-1"><strong>Tanggal:</strong> ${rec.date}</p>
                                    <p class="mb-1"><strong>Harga:</strong> $${rec.price.toLocaleString()}</p>
                                    <p class="mb-0"><strong>Rekomendasi:</strong> ${rec.strength}</p>
                                </div>
                            `;
                        });
                        $('#recommendations').html(recHtml);
                    } else {
                        $('#recommendations').html(`
                            <div class="alert alert-info">
                                Tidak ada sinyal beli yang kuat saat ini. Pertimbangkan Dollar-Cost Averaging.
                            </div>
                        `);
                    }
                    
                    // Render chart
                    const chartData = JSON.parse(response.chart);
                    Plotly.newPlot('price-chart', chartData.data, chartData.layout);
                } else {
                    alert('Error: ' + response.message);
                }
            },
            error: function(xhr, status, error) {
                alert('Terjadi kesalahan: ' + error);
            },
            complete: function() {
                $('#analyze-btn').html('<i class="fas fa-chart-line me-2"></i>Analisis Sekarang');
            }
        });
    });
    
    // Trigger initial analysis
    $('#analyze-btn').click();
});

function getAlertClass(type) {
    const alertClasses = {
        'Golden Cross': 'success',
        'RSI Oversold': 'danger',
        'Below SMA 20': 'primary'
    };
    return alertClasses[type] || 'secondary';
}

function getIconClass(type) {
    const iconClasses = {
        'Golden Cross': 'fas fa-crosshairs',
        'RSI Oversold': 'fas fa-arrow-down',
        'Below SMA 20': 'fas fa-arrow-circle-down'
    };
    return iconClasses[type] || 'fas fa-info-circle';
}
