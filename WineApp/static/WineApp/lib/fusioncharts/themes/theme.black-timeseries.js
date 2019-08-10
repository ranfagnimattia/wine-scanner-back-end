const themeColors = {
    background: "#1e1e2f",
    card: "#27293d",
    caption: "#ffffff",
    subCaption: "#dfdfdf",
    text: "#9a9a9a",
    subText: "#4B4B4B",
    tooltip: "#e9e9eb",
    // color1: "#1d8cf8",
    // color2: "#40a34e",
    // color3: "#ff893d",
    // color4: "#dc3545"
    color1: "#1d8cf8",
    color2: "#2dce89",
    color3: "#ff893d",
    color4: "#f5365c"
};

const themeBlackTimeseries = {
    chart: {
        paletteColors: [themeColors.color1, themeColors.color2, themeColors.color3, themeColors.color4].join(', '),
        multiCanvasTooltip: 1,
        baseFont: "Poppins, sans-serif",
        style: {
            text: {"font-family": "Poppins, sans-serif"},
            background: {fill: themeColors.card},
            canvas: {
                fill: themeColors.card,
                stroke: themeColors.text,
                "stroke-width": .5
            }
        }
    },
    tooltip: {
        style: {
            container: {
                "background-color": themeColors.tooltip,
                opacity: .9,
                "border-radius": "5px",
                padding: "7px"
            },
            text: {"font-family": "Poppins, sans-serif", "font-size": "13px", color: themeColors.subText},
            header: {
                "font-family": "Poppins, sans-serif",
                "font-size": "12px",
                color: "#000000",
                padding: "0px"
            },
            body: {padding: "0px"}
        }
    },
    navigator: {
        scrollbar: {
            style: {
                button: {fill: themeColors.subCaption},
                arrow: {fill: themeColors.text},
                track: {fill: themeColors.subCaption},
                grip: {visibility: 'hidden'},
                scroller: {fill: themeColors.text}
            }
        },
        window: {
            style: {
                handle: {fill: themeColors.text},
                "handle-grip": {visibility: 'hidden'},
                mask: {opacity: .25, stroke: themeColors.subText, "stroke-width": .55}
            }
        }
    },
    crossline: {
        style:
            {
                line: {stroke: themeColors.text, "stroke-width": 1, opacity: .6},
                label: {"font-family": "Poppins, sans-serif"}
            }
    },
    extensions: {
        standardRangeSelector: {
            style: {
                "button-text": {
                    fill: themeColors.text,
                    "font-family": "Poppins, sans-serif"
                },
                "button-text:hover": {fill: themeColors.caption, "font-family": "Poppins, sans-serif"},
                "button-text:active": {fill: themeColors.subCaption, "font-family": "Poppins, sans-serif"},
                separator: {stroke: themeColors.subText, "stroke-width": .5}
            }
        }, customRangeSelector: {
            style: {
                "title-text": {fill: themeColors.subCaption, "font-family": "Poppins, sans-serif"},
                "title-text:hover": {fill: themeColors.caption},
                "title-text:active": {fill: themeColors.caption},
                "title-icon": {fill: themeColors.subCaption, "font-family": "Poppins, sans-serif"},
                "title-icon:hover": {fill: themeColors.caption},
                "title-icon:active": {fill: themeColors.caption},
                container: {"background-color": themeColors.tooltip},
                label: {color: themeColors.background, "font-family": "Poppins, sans-serif"},
                input: {
                    "background-color": themeColors.card,
                    color: themeColors.text,
                    "border-radius": "3px"
                },
                "button-apply": {
                    color: themeColors.subCaption,
                    "background-color": themeColors.color1,
                    border: "none"
                },
                "button-apply:hover": {color: themeColors.caption},
                "button-cancel": {
                    color: themeColors.text,
                    "background-color": themeColors.card,
                    border: "none"
                },
                "button-cancel:hover": {color: themeColors.caption},
                "cal-header": {"font-family": "Poppins, sans-serif", "background-color": themeColors.color1},
                "cal-navprev": {"font-family": "Poppins, sans-serif", "font-size": "12px"},
                "cal-navnext": {"font-family": "Poppins, sans-serif", "font-size": "12px"},
                "cal-weekend": {"background-color": themeColors.background},
                "cal-days": {
                    "background-color": themeColors.background,
                    color: themeColors.caption,
                    "font-family": "Poppins, sans-serif",
                    border: "none"
                },
                "cal-date": {
                    "background-color": themeColors.card,
                    color: themeColors.subCaption,
                    "font-family": "Poppins, sans-serif",
                    border: "none"
                },
                "cal-date:hover": {
                    "background-color": themeColors.text,
                    color: themeColors.caption,
                    "font-family": "Poppins, sans-serif",
                    border: "none"
                },
                "cal-disableddate": {
                    "background-color": themeColors.card,
                    color: themeColors.text,
                    "font-family": "Poppins, sans-serif",
                    border: "none"
                },
                "cal-selecteddate": {
                    "background-color": themeColors.color1,
                    color: themeColors.caption,
                    "font-family": "Poppins, sans-serif"
                }
            }
        }
    },
    legend: {
        item: {
            style: {
                text: {
                    fill: themeColors.text,
                    "font-size": 13,
                    "font-family": "Poppins, sans-serif",
                    "font-weight": "600"
                }
            }
        }
    },
    xaxis: {
        style: {
            title: {"font-size": 14, "font-family": "Poppins, sans-serif", fill: themeColors.text},
            "grid-line": {stroke: themeColors.subText, "stroke-width": .55},
            "tick-mark-major": {stroke: themeColors.subText, "stroke-width": .5},
            "tick-mark-minor": {stroke: themeColors.subText, "stroke-width": .25},
            "label-major": {color: themeColors.text},
            "label-minor": {color: themeColors.text},
            "label-context": {color: themeColors.text, "font-family": "Poppins, sans-serif"}
        }
    },
    plotconfig: {
        column: {style: {"plot:hover": {opacity: .5}, "plot:highlight": {opacity: .75}}},
        line: {style: {plot: {"stroke-width": 2}, anchor: {"stroke-width": 0}}},
        area: {style: {anchor: {"stroke-width": 0}}}
    },
    yaxis: [{
        style: {
            title: {"font-size": 14, "font-family": "Poppins, sans-serif", fill: themeColors.text},
            "tick-mark": {stroke: themeColors.subText, "stroke-width": .5},
            "grid-line": {stroke: themeColors.subText, "stroke-width": .5},
            label: {color: themeColors.text}
        }
    }]
};