# THIS FILE GENERATES THE FIGURES 2 AND 3

import click
import logging
import numpy as np
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from lib.movingaverage import MovingAverage


@click.command()
@click.option('--a', default=7/12, help='Mean arrival rate')
@click.option('--nu', default=6, help='Mean service rate.')
@click.option('--J', default=30, help='J+1 is the number of queues of each component.')
@click.option('--init-A0', default=2400, help='Queue length at queue A0.')
@click.option('--init-Aj', default=0, help='Queue length at queue Aj.')
@click.option('--init-B0', default=0, help='Queue length at queue B0.')
@click.option('--init-Bj', default=0, help='Queue length at queue Bj.')
@click.option('--runtime', default=5 * 10 ** 5, help='Discrete time simulation length.')
@click.option('--save-to-file/--no-save-to-file', default=True, help='Enable saving pictures to files.', show_default=True)
@click.option('--output-dir', default="./output", help='Set the output directory for pictures.')
@click.option('--seed', default=8086, help='Seed used to generate random quantities.')
@click.option('--av', default=30, help='Windows parameter to compute moving averages.')
@click.option('--version', default='', help='Suffix to append to the output files. Example: "v1" ')
@click.option('--cut/--no-cut', default=True, help='Visualize the cut region.', show_default=True)
@click.option('--cut-level', default=6000, help='Denote a which level to start the cut.')
@click.option('--cache/--no-cache', default=True, help='Read the simulation data form a file.', show_default=True)
@click.option('--cache-dir', default="./cache", help='Set the cache directory for simulations.')
@click.option('--record/--no-record', default=True, help='Record simulation data and pictures to files.', show_default=True)
@click.option('--debug/--no-debug', default=False, help='Enable debugging behaviour.', show_default=True)
@click.option('--show-progress/--no-show-progress', default=True, help='Show percentage of simulation completed.', show_default=True)
def main(a, nu, j, init_a0, init_aj, init_b0, init_bj, runtime, save_to_file, output_dir, seed, av,
         version, cut, cut_level, cache, cache_dir, record, debug, show_progress):
    queue_A0 = queue_B0 = None
    queue_Aj = queue_Bj = None
    max_queue_Aj = max_queue_Bj = None
    avIn_queue_A0 = avOut_queue_A0 = avIn_queue_B0 = avOut_queue_B0 = None
    recording = []

    logging.basicConfig(format='%(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.DEBUG if debug else logging.INFO)
    logger.info(f'a={a}, nu={nu}, J={j}, init-A0={init_a0}')

    def set_seed(s):
        if s is None:
            np.random.seed(None)
            s = np.random.randint(0, 100000)
        logger.info(f'SEED: {s}')
        np.random.seed(s)

    def get_filename(prefix="simulation", suffix="", type=".pdf"):
        sx = suffix
        if suffix != "":
            sx = "_" + suffix
        return prefix \
               + '_J' + str(j) \
               + '_a' + str(a).replace('.', 'p')[0:4] \
               + '_nu' + str(nu) \
               + '_r' + str(runtime) \
               + '_seed' + str(seed) \
               + sx \
               + type

    def save_recording(dir):
        basedir = os.path.join(os.getcwd(), "cache") if dir is None else dir
        filename = get_filename(type=".npy")
        np.save(os.path.join(basedir, filename), recording)

    def load_recording(dir):
        basedir = os.path.join(os.getcwd(), "cache") if dir is None else dir
        filename = get_filename(type=".npy")
        return np.load(os.path.join(basedir, filename))

    def column(matrix, i, j=None):
        if j is not None:
            return [row[i][j] for row in matrix]
        return [row[i] for row in matrix]

    def rec():
        min_queue_Aj = min(queue_Aj)
        min_queue_Bj = min(queue_Bj)
        recording.append(
            [[queue_A0, max_queue_Aj, min_queue_Aj, avIn_queue_A0.get(), avOut_queue_A0.get()],
             [queue_B0, max_queue_Bj, min_queue_Bj, avIn_queue_B0.get(), avOut_queue_B0.get()],
             ])  # ** recording R3

    def find_regions(level=400, empty_A0=0):
        margin_left = 0  # for the cut window
        margin_right = 0.15  # for the cut window

        rec_queue_A0 = column(recording, 0, 0)
        rec_max_queue_Aj = column(recording, 0, 1)
        rec_queue_B0 = column(recording, 1, 0)
        rec_max_queue_Bj = column(recording, 1, 1)

        reach_level = 0
        for x in rec_queue_B0:
            if x >= level:
                break
            reach_level += 1

        reach_empty_queue_A0 = reach_level
        for x in rec_queue_A0[reach_level:]:
            if x <= empty_A0:
                break
            reach_empty_queue_A0 += 1

        previous_empty_queue_A0 = reach_level
        for x in range(reach_level):
            if rec_queue_A0[reach_level - x] <= empty_A0:
                break
            previous_empty_queue_A0 -= 1

        start_equilibrium = previous_empty_queue_A0
        for x in range(reach_level - previous_empty_queue_A0):
            if rec_queue_A0[previous_empty_queue_A0 + x] <= nu * rec_max_queue_Aj[previous_empty_queue_A0 + x]:
                break
            start_equilibrium += 1

        end_equilibrium = reach_empty_queue_A0
        for x in range(len(rec_queue_A0[reach_empty_queue_A0:])):
            if rec_queue_B0[reach_empty_queue_A0 + x] <= nu * rec_max_queue_Bj[reach_empty_queue_A0 + x]:
                break
            end_equilibrium += 1

        start = start_equilibrium - int((end_equilibrium - start_equilibrium) * margin_left)
        end = end_equilibrium + int((end_equilibrium - start_equilibrium) * margin_right)
        return [start, [start_equilibrium, reach_empty_queue_A0, end_equilibrium], end]

    def plot(show_cut=True, cut=False):
        start_cut = end_cut = None
        divisions = None

        ax = plt.axes()
        ax.tick_params(labelsize='xx-large')
        ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0), useMathText=True)
        ax.yaxis.offsetText.set_fontsize(16)
        if not cut:
            ax.ticklabel_format(axis="x", style="sci", scilimits=(0, 0), useMathText=True)
            ax.xaxis.offsetText.set_fontsize(16)

        if cut or show_cut:
            [start_cut, divisions, end_cut] = find_regions(cut_level, nu ** 2)
        if cut:
            [start, end] = [start_cut, end_cut]
            # plt.subplot(2, 1, 1)
        else:
            [start, end] = [0, runtime]
        t = range(start, end)

        # station A
        rec_scaled_queue_A0 = [x / nu for x in column(recording, 0, 0)[start:end]]
        rec_max_queue_Aj = column(recording, 0, 1)[start:end]
        rec_min_queue_Aj = column(recording, 0, 2)[start:end]

        tmp_label = '$Q_{A_0} / \\nu$'
        plt.plot(t, rec_scaled_queue_A0, lw=1, label=tmp_label, color='black')
        tmp_label = '$\\max_{j>0} Q_{A_j}$'
        plt.plot(t, rec_max_queue_Aj, lw=1, label=tmp_label, color="black", ls='--')
        tmp_label = '$\\min_{j>0} Q_{A_j}$'
        plt.plot(t, rec_min_queue_Aj, lw=1, label=tmp_label, color="black", ls='--')

        # station B
        rec_scaled_queue_B0 = [x / nu for x in column(recording, 1, 0)[start:end]]
        rec_max_queue_Bj = column(recording, 1, 1)[start:end]
        rec_min_queue_Bj = column(recording, 1, 2)[start:end]

        tmp_label = '$Q_{B_0} / \\nu$'
        plt.plot(t, rec_scaled_queue_B0, lw=1, label=tmp_label, color='gray')
        tmp_label = '$\\max_{j>0} Q_{B_j}$'
        plt.plot(t, rec_max_queue_Bj, lw=1, label=tmp_label, color="gray", ls='--')
        tmp_label = '$\\min_{j>0} Q_{B_j}$'
        plt.plot(t, rec_min_queue_Bj, lw=1, label=tmp_label, color="gray", ls='--')

        plt.legend(loc='upper left', fontsize=18, markerscale=0.85, numpoints=1, handlelength=4.5)

        # Annotations
        if cut:
            left, right = plt.xlim()  # return the current xlim
            plt.xlim(left * 0.974, right)  # set the xlim to left, right

            for x_div in divisions:
                plt.axvline(x=x_div, color='k', linestyle='--')

            ymin, ymax = plt.ylim()
            bbox_props = dict(boxstyle="circle, pad=0.3", fc="w", ec="0.5", alpha=0.9)
            plt.annotate('0', color='black', size='large', bbox=bbox_props,
                         xycoords="data", ha="center", va="center", xy=[divisions[0], ymax])
            plt.annotate('U', color='black', size='large', bbox=bbox_props,
                         xycoords="data", ha="center", va="center", xy=[divisions[1], ymax])
            plt.annotate('V', color='black', size='large', bbox=bbox_props,
                         xycoords="data", ha="center", va="center", xy=[divisions[2], ymax])

            # xticks
            plt.xticks(divisions, ["{:,}".format(_) for _ in divisions])

            ystart, yend = plt.gca().get_ylim()
            yticks = np.arange(0, yend, 500)
            yticks = np.append(yticks, rec_scaled_queue_A0[0])
            plt.yticks(yticks)

            # Put a legend to the right of the current axis
            plt.legend(loc='center left', fontsize=18, markerscale=0.85, numpoints=1, handlelength=4.5)

        elif show_cut:
            margin_vertical = 0.05  # for the cut window
            h = max([max(rec_scaled_queue_A0[start_cut:end_cut]), max(rec_scaled_queue_B0[start_cut:end_cut])])
            b = end_cut - start_cut
            ax.add_patch(patches.Rectangle(
                (start_cut, - h * margin_vertical),
                b, h * (1 + 2 * margin_vertical),
                fill=False, linestyle='-.'
            ))

            xticks = np.arange(0, runtime, runtime / 5)
            xticks = np.append(xticks, divisions[0])
            plt.xticks(xticks)

            ystart, yend = plt.gca().get_ylim()
            yticks = np.arange(0, yend, 1500)
            yticks = np.append(yticks, rec_scaled_queue_A0[start_cut])
            plt.yticks(yticks)

        plt.xlabel('time', fontsize='xx-large')

    def simulate(a, nu, j, runtime, init_a0=0, init_aj=0, init_b0=0, init_bj=0):
        nonlocal queue_A0, queue_B0
        nonlocal queue_Aj, queue_Bj, max_queue_Aj, max_queue_Bj
        nonlocal avIn_queue_A0, avOut_queue_A0, avIn_queue_B0, avOut_queue_B0
        nonlocal recording

        np.random.seed()

        queue_A0 = init_a0
        queue_Aj = np.full(j, init_aj)
        sum_queue_Aj = sum(queue_Aj)
        max_queue_Aj = max(queue_Aj)
        max_queue_A = max([queue_A0, max_queue_Aj])
        avIn_queue_A0 = MovingAverage(av)
        avOut_queue_A0 = MovingAverage(av)

        queue_B0 = init_b0
        queue_Bj = np.full(j, init_bj)
        sum_queue_Bj = sum(queue_Bj)
        max_queue_Bj = max(queue_Bj)
        max_queue_B = max([queue_B0, max_queue_Bj])
        avIn_queue_B0 = MovingAverage(av)
        avOut_queue_B0 = MovingAverage(av)

        logger.debug(f'maxA: {max_queue_A}, maxB: {max_queue_B}')

        for _time in range(runtime):

            if show_progress and (_time * 100 / runtime % 1 == 0):
                logger.info(f'{_time * 100 / runtime}% DONE')
            
            # arrivals at component A
            arrA = 0
            if np.random.random() < a:
                arrA = np.random.randint(0, j)
                queue_Aj[arrA] += 1
                sum_queue_Aj += 1

            # arrivals at component B
            arrB = 0
            if np.random.random() < a:
                arrB = np.random.randint(0, j)
                queue_Bj[arrB] += 1
                sum_queue_Bj += 1

            in_queue_A0 = 0
            in_queue_B0 = 0
            out_queue_A0 = 0
            out_queue_B0 = 0

            # Component A
            max_queue_Aj = max(queue_Aj)
            ix_max_queue_Aj = np.argmax(queue_Aj)
            if queue_A0 >= nu * max_queue_Aj:
                if queue_A0 > 0:
                    out_queue_A0 = 1
                    queue_A0 -= out_queue_A0
            else:
                svr_packets_A = min(nu, queue_Aj[ix_max_queue_Aj])
                queue_Aj[ix_max_queue_Aj] -= svr_packets_A
                sum_queue_Aj -= svr_packets_A
                in_queue_B0 = svr_packets_A
                queue_B0 += in_queue_B0

            # Comnponent B
            max_queue_Bj = max(queue_Bj)
            ix_max_queue_Bj = np.argmax(queue_Bj)
            if queue_B0 >= nu * max_queue_Bj:
                if queue_B0 > 0:
                    out_queue_B0 = 1
                    queue_B0 -= out_queue_B0
            else:
                svr_packets_B = min(nu, queue_Bj[ix_max_queue_Bj])
                queue_Bj[ix_max_queue_Bj] -= svr_packets_B
                sum_queue_Bj -= svr_packets_B
                in_queue_A0 = svr_packets_B
                queue_A0 += in_queue_A0

            avIn_queue_A0.push(in_queue_A0)
            avOut_queue_A0.push(out_queue_A0)
            avIn_queue_B0.push(in_queue_B0)
            avOut_queue_B0.push(out_queue_B0)

            if debug:
                max_queue_A = max([queue_A0, max_queue_Aj])
                max_queue_B = max([queue_B0, max_queue_Bj])
                logger.debug('arrA: {arrA}, arrB: {arrB}')
                logger.debug('maxA: {max_queue_A}, maxB: {max_queue_B}')

            rec()  # save data to recording variable

        if record:
            save_recording(cache_dir)

    if cache:
        logger.warning('Reading from CACHE')
        recording = load_recording(cache_dir)
    else:
        set_seed(seed)
        simulate(a, nu, j, runtime, init_a0, init_aj, init_b0, init_bj)

    basedir = os.path.expanduser("~") + '/Desktop/' if output_dir is None else output_dir

    plt.figure(figsize=(20, 6))
    plot(show_cut=cut)
    if save_to_file:
        filename = get_filename(suffix=version)
        plt.savefig(os.path.join(basedir, filename), bbox_inches='tight', dpi=300)
        filename = get_filename(suffix=version, type=".jpeg")
        plt.savefig(os.path.join(basedir, filename), bbox_inches='tight', dpi=300, format='JPG')
    plt.show()

    if cut:
        plt.figure(figsize=(20, 4))
        plot(cut=True)
        if save_to_file:
            filename = get_filename('cut-simulation', suffix=version)
            plt.savefig(os.path.join(basedir, filename), bbox_inches='tight', dpi=300)
            filename = get_filename('cut-simulation', suffix=version, type=".jpeg")
            plt.savefig(os.path.join(basedir, filename), bbox_inches='tight', dpi=300, format='JPG')
        plt.show()


if __name__ == "__main__":
    main()
