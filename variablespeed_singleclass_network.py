# THIS FILE GENERATES THE FIGURE 8

import click
import logging
import numpy as np
import os
import matplotlib.pyplot as plt
import time


@click.command()
@click.option('--a', default=1, help='Mean arrival rate')
@click.option('--m', default=20, help='Mean service time.')
@click.option('--epsilon', default=0.1791, help='The epsilon parameter.')
@click.option('--init-A0', default=55, help='Queue length at queue A0.')
@click.option('--runtime', default=5 * 10 ** 4, help='Discrete time simulation length.')
@click.option('--save-to-file/--no-save-to-file', default=True, help='Enable saving pictures to files.', show_default=True)
@click.option('--output-dir', default="./output", help='Set the output directory for pictures.')
@click.option('--seed', default=8086, help='Seed used to generate random quantities.')
@click.option('--version', default='', help='Suffix to append to the output files. Example: "v1" ')
@click.option('--cache/--no-cache', default=False, help='Read the simulation data form a file.', show_default=True)
@click.option('--cache-dir', default="./cache", help='Set the cache directory for simulations.')
@click.option('--record/--no-record', default=True, help='Record simulation data and pictures to files.', show_default=True)
@click.option('--debug/--no-debug', default=False, help='Enable debugging behaviour.', show_default=True)
@click.option('--show-progress/--no-show-progress', default=False, help='Show percentage of simulation completed.', show_default=True)
@click.option('--color/--no-color', default=False, help='Enable color in the pictures.', show_default=True)
def main(a, m, epsilon, init_a0, runtime, save_to_file, output_dir, seed,
         version, cache, cache_dir, record, debug, show_progress, color):
    len_queue_A0 = len_queue_A1 = None
    len_queue_B0 = len_queue_B1 = None
    recording = []

    logging.basicConfig(format='%(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.DEBUG if debug else logging.INFO)
    logger.info(f'a={a}, epsilon={epsilon}, m={m}, init-A0={init_a0}')

    def set_seed(s):
        if s is None:
            np.random.seed(None)
            s = np.random.randint(0, 100000)
        logger.info(f'SEED: {s}')
        np.random.seed(s)

    def rand_int(n):
        int_n = int(n)
        if np.random.random() <= n - int_n:
            return int_n + 1
        else:
            return int_n

    def get_filename(prefix="simulation", suffix="", type=".pdf"):
        sx = suffix
        if suffix != "":
            sx = "_" + suffix
        return prefix \
               + '_m' + str(m) \
               + '_a' + str(a).replace('.', 'p') \
               + '_eps' + str(epsilon).replace('.', 'p') \
               + '_r' + str(runtime) \
               + '_seed' + str(seed)  \
               + sx \
               + type

    def save_recording(_dir):
        _basedir = os.path.join(os.getcwd(), "cache") if _dir is None else _dir
        _filename = get_filename(type=".npy")
        np.save(os.path.join(_basedir, _filename), recording)

    def load_recording(_dir):
        _basedir = os.path.join(os.getcwd(), "cache") if _dir is None else _dir
        _filename = get_filename(type=".npy")
        return np.load(os.path.join(_basedir, _filename))

    def rec_r1(_time, interval=1, start_at=0):
        if _time > start_at and _time % interval == 0:
            recording.append([len_queue_A0 * epsilon, len_queue_A1,
                              len_queue_B0 * epsilon, len_queue_B1])

    # this is to record workloads
    def rec_r2(_time, interval=1, start_at=0):
        if _time > start_at and _time % interval == 0:
            recording.append([len_queue_A0 * epsilon, len_queue_A1 * m,
                              len_queue_B0 * epsilon, len_queue_B1] * m)

    def plot_r1(screen=True, color=False):
        # plot results:
        if screen:
            plt.figure(figsize=(7, 6))
            plt_title = 'm=' + str(m) + ', a=' + str(a) + ', '
            plt_title += '$\\epsilon$=' + str(epsilon)
            plt_title += ' .'
            plt.title(plt_title)
            plt.xlabel('time')
            plt.ylabel('queue-sizes')
            plt.ticklabel_format(axis="both", style="sci", scilimits=(4, 4), useMathText=True)
        else:
            plt.figure(figsize=(20, 6*1.5), dpi=300, constrained_layout=True)
            plt.ticklabel_format(axis="both", style="sci", scilimits=(4, 4), useMathText=True)
            plt.gca().yaxis.offsetText.set_fontsize(32)
            plt.gca().xaxis.offsetText.set_fontsize(32)
            plt.gca().tick_params(labelsize=36, length=15, pad=10)

        if color:
            n_fig = 2
            colors = ['red', 'blue']
            lines = ['-', '-']
        else:
            n_fig = 1
            colors = ['black', 'black', 'gray', 'gray']
            lines = ['--', '-', '--', '-']
            plt.gca().set_prop_cycle(color=colors, ls=lines)

        for i in range(4):
            if n_fig == 2 and i % 2 == 0:
                plt.subplot(211+int(i/2)).gca().set_prop_cycle(color=colors, ls=lines)

            label = '$Q_{' + chr(ord('A') + int(i / 2)) + '_' + str(i % 2) + '}' \
                    + ('' if i % 2 == 1 else '\\times \\epsilon') + '$'
            plot_data = [l[i] for l in recording]
            plt.plot(plot_data[0:runtime], lw=1, label=label)

            if (i+1) % int(4/n_fig) == 0:
                plt.legend(loc=2, fontsize=32, markerscale=0.85, numpoints=1, handlelength=4.5)

    def simulate(a, eps, M, init_A0, runtime):
        nonlocal len_queue_A0, len_queue_A1
        nonlocal len_queue_B0, len_queue_B1

        USE_GEOMETRIC = False

        len_queue_A0 = init_A0
        len_queue_A1 = 0
        len_queue_B0 = len_queue_B1 = 0

        cumulative_input_A = cumulative_output_A = 0
        cumulative_input_B = cumulative_output_B = 0

        for _time in range(runtime):

            if show_progress and (_time * 100 / runtime % 1 == 0):
                logger.info(f'{_time * 100 / runtime}% DONE')

            out_queue_A0 = out_queue_A1 = 0
            out_queue_B0 = out_queue_B1 = 0

            # Component A
            if len_queue_A0 >= len_queue_A1 / eps:  # eq. (60)
                # serving queue A0
                sigma_A0 = 1/eps
                service = rand_int(sigma_A0)
                out_queue_A0 = min(service, len_queue_A0)
                len_queue_A0 -= out_queue_A0
            else:
                # serving queue A1
                sigma_A1 = 1/(eps*eps)
                service = rand_int(sigma_A1)
                if USE_GEOMETRIC:
                    service -= np.random.geometric(1 / M)
                    while service >=0 and len_queue_A1 > 0:
                        len_queue_A1 -= 1
                        out_queue_A1 += 1
                        service -= np.random.geometric(1 / M)
                else:
                    served = min(np.random.binomial(service, 1 / M), len_queue_A1)
                    len_queue_A1 -= served
                    out_queue_A1 += served

            # Component B
            if len_queue_B0 >= len_queue_B1 / eps:  # eq. (60)
                # serving queue B0
                sigma_B0 = 1/eps
                service = rand_int(sigma_B0)
                out_queue_B0 = min(service, len_queue_B0)
                len_queue_B0 -= out_queue_B0
            else:
                # serving queue B1
                sigma_B1 = 1/(eps*eps)
                service = rand_int(sigma_B1)
                if USE_GEOMETRIC:
                    service -= np.random.geometric(1 / M)
                    while service >= 0 and len_queue_B1 > 0:
                        len_queue_B1 -= 1
                        out_queue_B1 += 1
                        service -= np.random.geometric(1 / M)
                else:
                    served = min(np.random.binomial(service, 1 / M), len_queue_B1)
                    len_queue_B1 -= served
                    out_queue_B1 += served

            # arrivals at queue A0 from outside
            arrivals_A0 = rand_int(a)
            cumulative_input_A += arrivals_A0
            len_queue_A0 += arrivals_A0

            # arrivals at queue B1 from queue A0
            len_queue_B1 += out_queue_A0

            # departures from queue B1
            cumulative_output_B += out_queue_B1

            # arrivals at queue B0 from outside
            arrivals_B0 = rand_int(a)
            cumulative_input_B += arrivals_B0
            len_queue_B0 += arrivals_B0

            # arrivals at queue A1 from queue B0
            len_queue_A1 += out_queue_B0

            # departures from queue A1
            cumulative_output_A += out_queue_A1

            logger.debug(f'[A0,B1,B0,A1]: {len_queue_A0, len_queue_B1, len_queue_B0, len_queue_A1}')
            logger.debug(f'cumInput A0: {cumulative_input_A}, cumOutput A1: {cumulative_output_A}')
            logger.debug(f'cumInput B0: {cumulative_input_B}, cumOutput B1: {cumulative_output_B}')

            rec(_time)  # save data to recording variable

        # Save recording to file
        if record:
            save_recording(cache_dir)

    # define the recording and the plotting functions
    rec = rec_r1
    plot = plot_r1

    if cache:
        logger.warning('Reading from CACHE')
        recording = load_recording(cache_dir)
    else:
        set_seed(seed)
        start = time.time()
        simulate(a, epsilon, m, init_a0, runtime)
        end = time.time()
        logger.info(f'Simulation time: {end - start}')

    plot(color=color)
    plt.show()

    if save_to_file:
        plot(screen=False, color=color)
        basedir = os.path.expanduser("~") + '/Desktop/' if output_dir is None else output_dir
        filename = get_filename(suffix=version)
        plt.savefig(os.path.join(basedir, filename), dpi=300)
        filename = get_filename(suffix=version, type=".jpeg")
        plt.savefig(os.path.join(basedir, filename), dpi=300, format='JPG')


if __name__ == "__main__":
    main(color=False)
