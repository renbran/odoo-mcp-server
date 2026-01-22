/** @odoo-module **/

import { Component, onMounted, useEffect, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ColumnChart extends Component {
  static template = "synconics_bi_dashboard.ColumnChart";
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
        this.render_column_chart();
      },
      () => [this.props.chartId, this.props.recordSets, this.props.data],
    );
    onMounted(() => {
      this.render_column_chart();
    });
  }

  render_column_chart() {
    var data = this.props.recordSets;
    if (this.root) {
      this.root.dispose();
    }
    if (typeof data == "object" && !Array.isArray(data)) {
      this.state.isError = true;
      this.state.errorMessage = data.message;
      return;
    }

    this.state.isError = false;
    this.state.errorMessage = false;
    this.root = window.am5_index.Root.new("column_chart__" + this.props.chartId);
    const theme = this.themeMap[this.props.theme];
    this.root.setThemes([theme.new(this.root)]);

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

    // Apply formatting to your data
    data = data.map((item) => ({
      ...item,
      category: formatLabel(item.category), // Assuming 'category' is your label field
    }));

    var chart = this.root.container.children.push(
      window.am5_xy.XYChart.new(this.root, {
        panX: false,
        panY: false,
        paddingLeft: 0,
        wheelX: "panX",
        wheelY: "zoomX",
        layout: this.root.verticalLayout,
      }),
    );

    var legend = chart.children.push(
      window.am5_index.Legend.new(this.root, {
        centerX: window.am5_index.p50,
        x: window.am5_index.p50,
      }),
    );

    var xRenderer = window.am5_xy.AxisRendererX.new(this.root, {
      cellStartLocation: 0.1,
      cellEndLocation: 0.9,
      minorGridEnabled: true,
    });

    xRenderer.labels.template.setAll({
      rotation: 0,
      centerY: window.am5_index.p50,
      centerX: window.am5_index.p50,
      paddingRight: 15,
      maxWidth: 100, // Set maximum width before wrapping
      oversizedBehavior: "wrap", // Enable text wrapping
      textAlign: "center",
    });

    var xAxis = chart.xAxes.push(
      window.am5_xy.CategoryAxis.new(this.root, {
        categoryField: "category",
        renderer: xRenderer,
        // tooltip: window.am5_index.Tooltip.new(this.root, {}),
      }),
    );

    xAxis.set(
      "tooltip",
      window.am5_index.Tooltip.new(this.root, {
        labelText: "{category}",
      }),
    );

    xRenderer.grid.template.setAll({
      location: 1,
    });

    xAxis.data.setAll(data);

    var yAxis = chart.yAxes.push(
      window.am5_xy.ValueAxis.new(this.root, {
        renderer: window.am5_xy.AxisRendererY.new(this.root, {
          strokeOpacity: 0.1,
        }),
      }),
    );

    var self = this;
    function makeSeries(name, fieldName) {
      var series = chart.series.push(
        window.am5_xy.ColumnSeries.new(self.root, {
          name: name,
          xAxis: xAxis,
          yAxis: yAxis,
          valueYField: fieldName,
          categoryXField: "category",
        }),
      );

      series.columns.template.setAll({
        tooltipText: "{name}, {categoryX}:{valueY}",
        width: window.am5_index.percent(90),
        tooltipY: 0,
        strokeOpacity: 0,
      });

      series.columns.template.events.on("click", function (ev) {
        if (self.props.update_chart) {
          self.props.update_chart(
            parseInt(self.props.chartId),
            "column_chart",
            ev.target.dataItem.dataContext,
          );
        }
      });

      series.data.setAll(data);
      series.appear();

      series.bullets.push(function () {
        return window.am5_index.Bullet.new(self.root, {
          locationY: 0,
          sprite: window.am5_index.Label.new(self.root, {
            text: "{valueY}",
            fill: self.root.interfaceColors.get("alternativeText"),
            centerY: 0,
            centerX: window.am5_index.p50,
            populateText: true,
          }),
        });
      });

      legend.data.push(series);
    }

    let keys = Object.keys(data[0]).filter(
      (k) => k !== "category" && k !== "record_id" && k !== "isSubGroupBy",
    );

    for (let key = 0; key < keys.length; key++) {
      makeSeries(keys[key], keys[key]);
    }

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
