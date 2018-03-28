from json import load
from config import OUTPUT_DIR, HAR_DIR
from os.path import join

import pygal
from pygal.style import CleanStyle, DarkStyle, LightColorizedStyle, RedBlueStyle
from pygal import Config
import logging

# svg to pdf with:
# cairosvg vimeo_e2_combinedplot.svg -o out.pdf


from vimeo_har import VimeoHar

logger = logging.getLogger(__name__)


def plot(name):
    metadata_path = join(OUTPUT_DIR, name+'_metadata.json')
    har_path = join(HAR_DIR, name+'_har.json')

    metaplot(name, metadata_path)
    harplot(name, har_path)
    combined_plot(name, metadata_path, har_path)


def metaplot(name, path):
    logger.info(f'Loaded file {path} for plotting')

    metadata = load(open(path))

    line_chart = pygal.XY()
    line_chart.title = f'Metadata {name}'

    line_chart.y_labels = [0, 240, 360, 480, 720, 1080]
    line_chart.x_labels = (int(e['time']) for e in metadata)

    x_points = meta_to_pyglot(metadata)
    line_chart.add('Metadata', x_points)  # Add some values

    path = join(OUTPUT_DIR, name+'_metaplot')
    line_chart.render_to_file(path+'.svg')
    line_chart.render_to_png(path+'.png')
    logger.info(f'Created plot at: {path}.png')


def meta_to_pyglot(data):
    """ Converts the metadata format to something plottable
    """
    # generate missing points
    duration = int(data[-1]['time'])
    x_points = []
    y = 0
    output = True
    for i in range(0, duration+1):
        match = [e for e in data if int(e['time']) == i]
        if match:
            x_points.append((i, y))
            output = True
            y = match[0]['quality'][1]

        elif output:
            output = False
            x_points.append((i, y))

        else:
            x_points.append(None)
    return x_points


def harplot(name, path):
    if 'vimeo' in name.lower():
        data = VimeoHar(path).plot_time_quality()
    else:
        logger.error(f'harploter didn\'t recognize name {name} and does not know this format')
        return

    line_chart = pygal.XY()
    line_chart.title = f'Har {name}'

    line_chart.y_labels = [0, 240, 360, 480, 720, 1080]
    # change_points = [point[0] for point in data if point[1]] + [data[-1][0]]
    # line_chart.x_labels = change_points

    line_chart.add('Hardata', data)  # Add some values

    path = join(OUTPUT_DIR, name + '_harplot')
    line_chart.render_to_file(path + '.svg')
    line_chart.render_to_png(path + '.png')
    logger.info(f'Created plot at: {path}.png')


def combined_plot(name, metapath, harpath):
    if 'vimeo' in name.lower():
        hardata = VimeoHar(harpath).plot_time_quality()
    else:
        logger.error(f'harploter didn\'t recognize name {name} and does not know this format')
        return

    metadata = load(open(metapath))

    # generel setup
    line_chart = pygal.XY(legend_at_bottom=True, stroke_style={'width': 5})


    # line_chart.title = f'Vimeo quality by javascript and request headers'

    line_chart.y_labels = [0, 240, 360, 480, 720, 1080]

    line_chart.add('javascript api', meta_to_pyglot(metadata))  # Add some values
    line_chart.add('request headers', hardata)                    # Add some values

    path = join(OUTPUT_DIR, name + '_combinedplot')
    line_chart.render_to_file(path + '.svg')
    line_chart.render_to_png(path + '.png', dpi=720)
    logger.info(f'Created plot at: {path}.png')


if __name__ == '__main__':
    plot('vimeo_e2')
