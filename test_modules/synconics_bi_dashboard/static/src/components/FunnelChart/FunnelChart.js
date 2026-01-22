/** @odoo-module **/

import { Component, onMounted, useEffect, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class FunnelChart extends Component {
  static template = "synconics_bi_dashboard.FunnelChart";
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
        this.render_funnel_chart();
      },
      () => [this.props.chartId, this.props.recordSets, this.props.data],
    );
    onMounted(() => {
      this.render_funnel_chart();
    });
  }

  render_funnel_chart() {
    let data = this.props.recordSets;
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
    this.root = window.am5_index.Root.new("funnel_chart__" + this.props.chartId);
    const theme = this.themeMap[this.props.theme];
    this.root.setThemes([theme.new(this.root)]);

    var chart = this.root.container.children.push(
      window.am5_percent.SlicedChart.new(this.root, {
        layout: this.root.verticalLayout,
      }),
    );

    var series = chart.series.push(
      window.am5_percent.FunnelSeries.new(this.root, {
        alignLabels: false,
        orientation: "vertical",
        valueField: "value",
        categoryField: "category",
      }),
    );
    var self = this;
    series.slices.template.events.on("click", function (ev) {
      if (self.props.update_chart) {
        self.props.update_chart(
          parseInt(self.props.chartId),
          "funnel_chart",
          ev.target.dataItem.dataContext,
        );
      }
    });

    series.data.setAll(data);

    series.appear();

    var legend = chart.children.push(
      window.am5_index.Legend.new(this.root, {
        centerX: window.am5_index.p50,
        x: window.am5_index.p50,
        marginTop: 15,
        marginBottom: 15,
      }),
    );

    legend.data.setAll(series.dataItems);

    chart.appear(1000, 100);
    let exporting = window.am5_exporting.Exporting.new(this.root, {
      filePrefix: "my_chart",
      dataSource: chart.series.getIndex(0),
    });
    this.root.events.once("frameended", () => {
      if (this.props.export) {
        this.props.export(exporting);
      }
    });
  }
}
