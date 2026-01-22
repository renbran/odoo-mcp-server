/** @odoo-module **/

import { Component, onMounted, useEffect, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class BarChart extends Component {
  static template = "synconics_bi_dashboard.BarChart";
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
    // this.exporting = false;
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
        this.render_bar_chart();
      },
      () => [this.props.chartId, this.props.recordSets, this.props.data],
    );
    onMounted(() => {
      this.render_bar_chart();
    });
  }
  render_bar_chart() {
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
    this.root = window.am5_index.Root.new("bar_chart__" + this.props.chartId);
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

    if (data[0].isSubGroupBy) {
      var chart = this.root.container.children.push(
        window.am5_xy.XYChart.new(this.root, {
          panX: false,
          panY: false,
          wheelX: "none",
          wheelY: "none",
          layout: this.root.horizontalLayout,
          paddingLeft: 0,
        }),
      );

      var legendData = [];
      var legend = chart.children.push(
        window.am5_index.Legend.new(this.root, {
          nameField: "name",
          fillField: "color",
          strokeField: "color",
          //centerY: window.am5_index.p50,
          marginLeft: 20,
          y: 20,
          layout: this.root.verticalLayout,
          clickTarget: "none",
        }),
      );

      var keys_obj = {};

      function transformData(currentData) {
        const result = [];

        currentData.forEach((record) => {
          const { category, record_id, ...valueFields } = record;

          Object.entries(valueFields).forEach(([valueTitle, value]) => {
            if (value > 0) {
              result.push({
                category,
                record_id,
                value_title: valueTitle + "(" + record_id + ")",
                value: value,
              });
            }
          });
        });

        return result;
      }

      const transformedData = transformData(data);
      for (let tData = 0; tData < transformedData.length; tData++) {
        if (transformedData[tData].value_title != "isSubGroupBy") {
          keys_obj[transformedData[tData].category] =
            transformedData[tData].value_title;
        }
      }
      if (!transformedData.length) {
        this.root.dispose();
        this.state.isError = true;
        this.state.errorMessage = "No Data to display!";
      }

      var yAxis = chart.yAxes.push(
        window.am5_xy.CategoryAxis.new(this.root, {
          categoryField: "value_title",
          renderer: window.am5_xy.AxisRendererY.new(this.root, {
            minGridDistance: 10,
            minorGridEnabled: true,
          }),
          tooltip: window.am5_index.Tooltip.new(this.root, {}),
        }),
      );

      yAxis.get("renderer").labels.template.setAll({
        fontSize: 12,
        location: 0.5,
      });
      yAxis.data.setAll(transformedData);

      var xAxis = chart.xAxes.push(
        window.am5_xy.ValueAxis.new(this.root, {
          renderer: window.am5_xy.AxisRendererX.new(this.root, {}),
          tooltip: window.am5_index.Tooltip.new(this.root, {}),
        }),
      );

      var series = chart.series.push(
        window.am5_xy.ColumnSeries.new(this.root, {
          xAxis: xAxis,
          yAxis: yAxis,
          valueXField: "value",
          categoryYField: "value_title",
          tooltip: window.am5_index.Tooltip.new(this.root, {
            pointerOrientation: "horizontal",
          }),
        }),
      );

      series.columns.template.setAll({
        tooltipText: "{categoryY}: [bold]{valueX}[/]",
        width: window.am5_index.percent(90),
        strokeOpacity: 0,
      });

      var color_indexes = {};
      var color_counter = 0;
      for (var counter = 0; counter < data.length; counter++) {
        color_indexes[data[counter].category] = chart
          .get("colors")
          .getIndex(color_counter);
        color_counter = color_counter + 1;
      }

      series.columns.template.adapters.add("fill", function (fill, target) {
        if (target.dataItem) {
          return color_indexes[target.dataItem.dataContext.category];
        }
        return fill;
      });
      var self = this;
      series.columns.template.events.on("click", function (ev) {
        if (self.props.update_chart) {
          self.props.update_chart(
            parseInt(self.props.chartId),
            "bar_chart",
            ev.target.dataItem.dataContext,
          );
        }
      });

      series.data.setAll(transformedData);

      function createRange(label, category, color) {
        var rangeDataItem = yAxis.makeDataItem({
          category: category,
        });

        var range = yAxis.createAxisRange(rangeDataItem);

        rangeDataItem.get("label").setAll({
          fill: color,
          text: label,
          location: 1,
          fontWeight: "bold",
          dx: -130,
        });

        rangeDataItem.get("grid").setAll({
          stroke: color,
          strokeOpacity: 1,
          location: 1,
        });

        rangeDataItem.get("tick").setAll({
          stroke: color,
          strokeOpacity: 1,
          location: 1,
          visible: true,
          length: 130,
        });

        legendData.push({ name: label, color: color });
      }

      for (var counter = 0; counter < data.length; counter++) {
        createRange(
          data[counter].category,
          keys_obj[data[counter].category],
          color_indexes[data[counter].category],
        );
      }

      legend.data.setAll(legendData);
      var cursor = chart.set(
        "cursor",
        window.am5_xy.XYCursor.new(this.root, {
          xAxis: xAxis,
          yAxis: yAxis,
        }),
      );

      series.appear();
      chart.appear(1000, 100);
    } else {
      var chart = this.root.container.children.push(
        window.am5_xy.XYChart.new(this.root, {
          panX: false,
          panY: false,
          wheelX: "panX",
          wheelY: "zoomX",
          paddingLeft: 0,
          layout: this.root.verticalLayout,
        }),
      );

      var yAxisRenderer = window.am5_xy.AxisRendererY.new(this.root, {
        inversed: true,
        cellStartLocation: 0.1,
        cellEndLocation: 0.9,
        minorGridEnabled: true,
      });

      yAxisRenderer.labels.template.setAll({
        rotation: -40, // Tilt upward (-30 or -45 also possible)
        centerY: window.am5_index.p50,
        centerX: window.am5_index.p100,
        paddingRight: 10,
      });

      var yAxis = chart.yAxes.push(
        window.am5_xy.CategoryAxis.new(this.root, {
          categoryField: "category",
          renderer: yAxisRenderer,
        }),
      );

      yAxis.data.setAll(data);

      var xAxisRenderer = window.am5_xy.AxisRendererX.new(this.root, {
        strokeOpacity: 0.1,
        minGridDistance: 50,
      });

      xAxisRenderer.labels.template.setAll({
        rotation: -30, // Optional
        centerX: window.am5_index.p50,
        centerY: window.am5_index.p100,
        paddingTop: 10,
      });

      var xAxis = chart.xAxes.push(
        window.am5_xy.ValueAxis.new(this.root, {
          renderer: xAxisRenderer,
          min: 0,
        }),
      );

      var self = this;

      function createSeries(field, name) {
        var series = chart.series.push(
          window.am5_xy.ColumnSeries.new(self.root, {
            name: name,
            xAxis: xAxis,
            yAxis: yAxis,
            valueXField: field,
            categoryYField: "category",
            sequencedInterpolation: true,
            tooltip: window.am5_index.Tooltip.new(self.root, {
              pointerOrientation: "horizontal",
              labelText: "[bold]{name}[/]\n{categoryY}: {valueX}",
            }),
          }),
        );

        series.columns.template.setAll({
          height: window.am5_index.p100,
          strokeOpacity: 0,
        });
        series.columns.template.events.on("click", function (ev) {
          if (self.props.update_chart) {
            self.props.update_chart(
              parseInt(self.props.chartId),
              "bar_chart",
              ev.target.dataItem.dataContext,
            );
          }
        });

        series.bullets.push(function () {
          var bullet = window.am5_index.Bullet.new(self.root, {
            locationX: 1,
            locationY: 0.5,
            sprite: window.am5_index.Label.new(self.root, {
              centerY: window.am5_index.p50,
              text: "{valueX}",
              populateText: true,
            }),
          });

          // Hide zero values
          bullet.get("sprite").adapters.add("text", function (text, target) {
            if (target.dataItem && target.dataItem.get("valueX") === 0) {
              return "";
            }
            return text;
          });

          return bullet;
        });

        series.bullets.push(function () {
          return window.am5_index.Bullet.new(self.root, {
            locationX: 1,
            locationY: 0.5,
            sprite: window.am5_index.Label.new(self.root, {
              centerX: window.am5_index.p100,
              centerY: window.am5_index.p50,
              text: "{name}",
              fill: window.am5_index.color(0xffffff),
              populateText: true,
            }),
          });
        });

        series.data.setAll(data);
        series.appear();

        return series;
      }
      let keys = Object.keys(data[0]).filter(
        (k) => k !== "category" && k !== "record_id" && k !== "isSubGroupBy",
      );
      for (let key = 0; key < keys.length; key++) {
        createSeries(keys[key], keys[key]);
      }

      var legend = chart.children.push(
        window.am5_index.Legend.new(this.root, {
          centerX: window.am5_index.p50,
          x: window.am5_index.p50,
        }),
      );

      legend.data.setAll(chart.series.values);

      var cursor = chart.set(
        "cursor",
        window.am5_xy.XYCursor.new(this.root, {
          behavior: "zoomY",
        }),
      );
      cursor.lineY.set("forceHidden", true);
      cursor.lineX.set("forceHidden", true);

      chart.appear(1000, 100);
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
