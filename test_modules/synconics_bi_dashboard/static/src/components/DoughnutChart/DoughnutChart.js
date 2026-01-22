/** @odoo-module **/

import { Component, onMounted, useEffect, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class DoughnutChart extends Component {
  static template = "synconics_bi_dashboard.DoughnutChart";
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
        this.render_doughnut_chart();
      },
      () => [this.props.chartId, this.props.recordSets, this.props.data],
    );
    onMounted(() => {
      this.render_doughnut_chart();
    });
  }

  render_doughnut_chart() {
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
    this.root = window.am5_index.Root.new("doughnut_chart__" + this.props.chartId);
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
    var chartContainer = this.root.container.children.push(
      window.am5_index.Container.new(this.root, {
        layout: this.root.horizontalLayout,
        width: window.am5_index.percent(100),
        height: window.am5_index.percent(100),
      }),
    );

    var chart = chartContainer.children.push(
      window.am5_percent.PieChart.new(this.root, {
        layout: this.root.verticalLayout,
        innerRadius: window.am5_index.percent(40),
      }),
    );

    let keys = Object.keys(data[0]).filter(
      (k) => k !== "category" && k !== "record_id" && k !== "isSubGroupBy",
    );
    var self = this;

    var legend = chartContainer.children.push(
      window.am5_index.Legend.new(this.root, {
        width: 300,
        centerY: window.am5_index.percent(50),
        y: window.am5_index.percent(50),
        layout: this.root.verticalLayout,
        useDefaultMarker: true,
      }),
    );

    legend.markerRectangles.template.setAll({
      width: 15,
      height: 15,
      cornerRadiusTL: 5,
      cornerRadiusTR: 5,
      cornerRadiusBL: 5,
      cornerRadiusBR: 5,
    });

    for (let key = 0; key < keys.length; key++) {
      var series = chart.series.push(
        window.am5_percent.PieSeries.new(this.root, {
          valueField: keys[key],
          name: keys[key],
          categoryField: "category",
          alignLabels: false,
        }),
      );
      var bgColor = this.root.interfaceColors.get("background");
      series.slices.template.events.on("click", function (ev) {
        if (self.props.update_chart) {
          self.props.update_chart(
            parseInt(self.props.chartId),
            "doughnut_chart",
            ev.target.dataItem.dataContext,
          );
        }
      });
      series.ticks.template.setAll({ forceHidden: true });
      series.labels.template.setAll({ forceHidden: true });
      series.slices.template.setAll({
        stroke: bgColor,
        strokeWidth: 2,
        tooltipText: "{name}, {category}:{value}",
      });
      series.slices.template.states.create("hover", { scale: 0.95 });
      series.data.setAll(data);
      series.appear(1000, 100);
      legend.data.push(series);
      legend.data.setAll(series.dataItems);
    }
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
