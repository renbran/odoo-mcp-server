/** @odoo-module **/

import { Component, onMounted, useEffect, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class MapChart extends Component {
  static template = "synconics_bi_dashboard.MapChart";
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
        this.render_map_chart();
      },
      () => [this.props.chartId, this.props.recordSets, this.props.data],
    );
    onMounted(() => {
      this.render_map_chart();
    });
  }

  async render_map_chart() {
    let data = this.props.recordSets;
    if (typeof data == "object" && !Array.isArray(data)) {
      this.state.isError = true;
      this.state.errorMessage = data.message;
      return;
    }

    this.state.isError = false;
    this.state.errorMessage = false;
    if (this.root) {
      this.root.dispose();
    }

    this.root = window.am5_index.Root.new("map_chart__" + this.props.chartId);
    this.root.setThemes([window.am5_Animated.new(this.root)]);
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
      window.am5_map.MapChart.new(this.root, {}),
    );

    var polygonSeries = chart.series.push(
      window.am5_map.MapPolygonSeries.new(this.root, {
        geoJSON: window.am5_worldLow,
        exclude: ["AQ"],
      }),
    );

    var bubbleSeries = chart.series.push(
      window.am5_map.MapPointSeries.new(this.root, {
        valueField: "value",
        calculateAggregates: true,
        polygonIdField: "id",
      }),
    );

    var circleTemplate = window.am5_index.Template.new({});

    bubbleSeries.bullets.push(function (root, series, dataItem) {
      var container = window.am5_index.Container.new(root, {});

      var circle = container.children.push(
        window.am5_index.Circle.new(
          root,
          {
            radius: 20,
            fillOpacity: 0.7,
            fill: window.am5_index.color(0xff0000),
            cursorOverStyle: "pointer",
            tooltipText: `{name}: [bold]{value}[/]`,
          },
          circleTemplate,
        ),
      );

      var countryLabel = container.children.push(
        window.am5_index.Label.new(root, {
          text: "{name}",
          paddingLeft: 5,
          populateText: true,
          fontWeight: "bold",
          fontSize: 13,
          centerY: window.am5_index.p50,
        }),
      );

      circle.on("radius", function (radius) {
        countryLabel.set("x", radius);
      });

      return window.am5_index.Bullet.new(root, {
        sprite: container,
        dynamic: true,
      });
    });

    bubbleSeries.bullets.push(function (root, series, dataItem) {
      return window.am5_index.Bullet.new(root, {
        sprite: window.am5_index.Label.new(root, {
          text: "{value}",
          fill: window.am5_index.color(0xffffff),
          populateText: true,
          centerX: window.am5_index.p50,
          centerY: window.am5_index.p50,
          textAlign: "center",
        }),
        dynamic: true,
      });
    });

    bubbleSeries.set("heatRules", [
      {
        target: circleTemplate,
        dataField: "value",
        min: 35,
        max: 35,
        minValue: 35,
        maxValue: 35,
        key: "radius",
      },
    ]);

    bubbleSeries.data.setAll(data);

    let exporting = window.am5_exporting.Exporting.new(this.root, {
      filePrefix: "my_chart",
      dataSource: chart.series.getIndex(0),
    });

    this.root.events.once("frameended", () => {
      if (this.props.export) {
        this.props.export(exporting);
      }
    });

    updateData();

    function updateData() {
      for (var i = 0; i < bubbleSeries.dataItems.length; i++) {
        bubbleSeries.data.setIndex(i, {
          value: data[i].value,
          id: data[i].id,
          name: data[i].name,
        });
      }
    }
  }
}
