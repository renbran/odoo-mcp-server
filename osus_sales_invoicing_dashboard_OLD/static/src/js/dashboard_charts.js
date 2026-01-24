/** @odoo-module **/
/**
 * Smart dashboard charts: renders JSON datasets from fields into Chart.js.
 */
import { registry } from '@web/core/registry';
import { loadJS } from '@web/core/assets';
import { Component, onMounted, onWillUpdateProps, onWillUnmount, useRef } from '@odoo/owl';
import { standardFieldProps } from '@web/views/fields/standard_field_props';

const fieldRegistry = registry.category('fields');

async function ensureChartLib() {
    if (window.Chart) {
        return window.Chart;
    }
    await loadJS('/web/static/lib/Chart/Chart.js');
    return window.Chart;
}

class DashboardChart extends Component {
    static template = 'osus_sales_invoicing_dashboard.DashboardChart';
    static props = {
        ...standardFieldProps,
        options: { type: Object, optional: true },
    };

    setup() {
        this.canvasRef = useRef('canvas');
        this.chart = null;
        onMounted(() => this._renderChart());
        onWillUpdateProps(() => this._renderChart());
        onWillUnmount(() => this._destroyChart());
    }

    async _renderChart() {
        const chartData = this.props.record.data[this.props.name];

        // Get options from props (passed from view)
        const viewOptions = this.props.options || {};
        const chartType = viewOptions.chartType || 'bar';
        const title = viewOptions.title || '';

        if (!chartData || !chartData.labels || !chartData.labels.length) {
            this._destroyChart();
            return;
        }

        const Chart = await ensureChartLib();
        this._destroyChart();

        if (!this.canvasRef.el) {
            return;
        }

        const ctx = this.canvasRef.el.getContext('2d');
        this.chart = new Chart(ctx, {
            type: chartType,
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: true, position: 'bottom' },
                    title: { display: Boolean(title), text: title },
                },
                scales: chartType === 'bar' || chartType === 'line' ? {
                    x: { ticks: { autoSkip: true, maxRotation: 45 } },
                    y: { beginAtZero: true },
                } : {},
            },
        });
    }

    _destroyChart() {
        if (this.chart) {
            this.chart.destroy();
            this.chart = null;
        }
    }
}

export const dashboardChart = {
    component: DashboardChart,
    supportedTypes: ['json'],
    extractProps: ({ attrs, field }) => {
        return {
            options: attrs.options,
        };
    },
};

fieldRegistry.add('osus_dashboard_chart', dashboardChart);
