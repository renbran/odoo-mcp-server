/** @odoo-module **/

import { Component, onMounted, useEffect, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ScatterChart extends Component {
  static template = "synconics_bi_dashboard.ScatterChart";
  static props = {
    chartId: String,
    name: String,
    isDirty: { optional: true, type: Boolean },
    data: { optional: true, type: Object },
    update_chart: { optional: true, type: Function },
    theme: String,
    recordSets: Object,
    export: { optional: true, type: Function },
  };

  setup() {
    this.orm = useService("orm");
    this.root = null;
    this.themeMap = {
      animated: window.am5_Animated,
      frozen: window.am5_Frozen,
      kelly: window.am5_Kelly,
      material: window.am5_Material,
      moonrise: window.am5_Moonrise,
      spirited: window.am5_Spirited,
    };
    this.state = useState({ isError: false, errorMessage: false });
    useEffect(
      () => {
        this.render_scatter_chart();
      },
      () => [this.props.chartId, this.props.recordSets, this.props.data],
    );
    onMounted(() => {
      this.render_scatter_chart();
    });
  }

  async render_scatter_chart() {
    let rawData = this.props.recordSets;
    if (this.root) {
      this.root.dispose();
    }
    if (typeof rawData == "object" && !Array.isArray(rawData)) {
      this.state.isError = true;
      this.state.errorMessage = rawData.message;
      return;
    }

    this.state.isError = false;
    this.state.errorMessage = false;
    this.root = window.am5_index.Root.new("scatter_chart__" + this.props.chartId);
    const theme = this.themeMap[this.props.theme];
    const formatLabel = (text, maxLength = 15) => {
      if (!text) return text;
      if (typeof text !== "string") return text;
      if (text.length <= maxLength) return text;
      return (
        text
          .replace(/\[/g, "(")
          .replace(/\]/g, ")")
          .substring(0, maxLength - 3) + "..."
      );
    };

    // Apply formatting to your rawData
    rawData = rawData.map((item) => ({
      ...item,
      category: formatLabel(item.category), // Assuming 'category' is your label field
    }));
    this.root.setThemes([theme.new(this.root)]);
    let valueTypes = [];
    let companies = new Set();
    Object.keys(rawData[0]).forEach((key) => {
      if (!["category", "record_id", "isSubGroupBy"].includes(key)) {
        let parts = key.split(" - ");
        companies.add(parts[0]);
        if (!valueTypes.includes(parts[1])) {
          valueTypes.push(parts[1]);
        }
      }
    });
    companies = [...companies];
    let chartData = rawData.map((item, index) => {
      let obj = {
        index: index + 1,
        category: item.category,
        record_id: item.record_id,
      };
      companies.forEach((company) => {
        valueTypes.forEach((type) => {
          const key = `${company} - ${type}`;
          if (item[key] != null) {
            obj[`${company}_${type}`] = item[key];
          }
        });
      });

      return obj;
    });

    chartData.unshift({
      category: "0",
      ...Object.fromEntries(
        companies.flatMap((company) =>
          valueTypes.map((type) => [`${company}_${type}`, 0]),
        ),
      ),
    });
    // Create chart container
    var chart = this.root.container.children.push(
      window.am5_xy.XYChart.new(this.root, {
        panX: true,
        panY: true,
        wheelY: "zoomXY",
        pinchZoomX: true,
        pinchZoomY: true,
      }),
    );

    // Create X Axis (category-based)
    var xAxis = chart.xAxes.push(
      window.am5_xy.CategoryAxis.new(this.root, {
        categoryField: "category",
        renderer: window.am5_xy.AxisRendererX.new(this.root, {
          minGridDistance: 30,
          cellStartLocation: 0.1,
          cellEndLocation: 0.9,
        }),
        tooltip: window.am5_index.Tooltip.new(this.root, {}),
      }),
    );

    xAxis.get("renderer").labels.template.setAll({
      rotation: -20, // rotate label down to the right
      centerX: window.am5_index.p100,
      centerY: window.am5_index.p50,
      paddingRight: 10,
    });

    xAxis.data.setAll(chartData);

    // Create Y Axis (value-based)
    var yAxis = chart.yAxes.push(
      window.am5_xy.ValueAxis.new(this.root, {
        renderer: window.am5_xy.AxisRendererY.new(this.root, {}),
        tooltip: window.am5_index.Tooltip.new(this.root, {}),
      }),
    );

    // Create dynamic series
    var self = this;
    companies.forEach((company) => {
      valueTypes.forEach((type, i) => {
        const field = `${company}_${type}`;
        const series = chart.series.push(
          window.am5_xy.LineSeries.new(self.root, {
            name: `${company} (${type})`,
            xAxis: xAxis,
            yAxis: yAxis,
            categoryXField: "category",
            valueYField: field,
            tooltip: window.am5_index.Tooltip.new(self.root, {
              labelText: "{category}\n" + `${company} (${type}): {valueY}`,
            }),
          }),
        );
        series.bullets.push(function () {
          let shape = window.am5_index.Triangle.new(self.root, {
            fill: series.get("fill"),
            width: 12,
            height: 10,
            rotation: i === 0 ? 0 : 180,
            cursorOverStyle: "pointer",
          });
          shape.events.on("click", function (ev) {
            const dataItem = ev.target.dataItem;
            const dataContext = dataItem?.dataContext;

            if (dataContext && self.props.update_chart) {
              self.props.update_chart(
                parseInt(self.props.chartId),
                "scatter_chart",
                dataContext,
              );
            }
          });

          return window.am5_index.Bullet.new(self.root, {
            sprite: shape,
          });
        });

        series.data.setAll(chartData);
        series.appear(1000);
      });
    });

    // Add cursor
    chart.set(
      "cursor",
      window.am5_xy.XYCursor.new(this.root, {
        xAxis: xAxis,
        yAxis: yAxis,
        behavior: "zoomX",
        snapToSeries: chart.series.values,
      }),
    );

    // Optional: Add legend
    chart.children
      .push(
        window.am5_index.Legend.new(this.root, {
          centerX: window.am5_index.p50,
          x: window.am5_index.p50,
        }),
      )
      .data.setAll(chart.series.values);

    // Animate chart
    chart.appear(1000, 100);
    let exporting = window.am5_exporting.Exporting.new(this.root, {
      filePrefix: "my_chart",
      dataSource: chart.series.getIndex(0), // optional
    });
    this.root.events.once("frameended", () => {
      if (this.props.export) {
        this.props.export(exporting);
      }
    });
  }
}
