from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm


def simulate_trajectory(v, omega, duration=10.0, dt=0.05):
    steps = int(duration / dt)
    x, y, theta = 0.0, 0.0, 0.0
    xs, ys = [x], [y]
    for _ in range(steps):
        x += v * np.cos(theta) * dt
        y += v * np.sin(theta) * dt
        theta += omega * dt
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)


PROFILES = [
    ('Tutorial default  v=0.2, w=0.5',  0.2,  0.5),
    ('Tighter circle    v=0.2, w=1.0',  0.2,  1.0),
    ('Wide arc          v=0.4, w=0.3',  0.4,  0.3),
    ('Fast straight     v=0.5, w=0.0',  0.5,  0.0),
    ('Counter-CW        v=0.2, w=-0.5', 0.2, -0.5),
]


def main(args=None) -> None:
    colors = cm.tab10(np.linspace(0, 0.9, len(PROFILES)))
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    ax_xy, ax_dist = axes

    for (label, v, omega), color in zip(PROFILES, colors):
        xs, ys = simulate_trajectory(v, omega, duration=15.0)
        ax_xy.plot(xs, ys, linewidth=2, color=color, label=label)
        ax_xy.scatter([xs[0]], [ys[0]], c=[color], s=80, marker='o', zorder=5)
        ax_xy.scatter([xs[-1]], [ys[-1]], c=[color], s=80, marker='X', zorder=5)
        t = np.linspace(0, 15.0, len(xs))
        dists = np.cumsum(
            np.sqrt(np.diff(xs, prepend=xs[0])**2 + np.diff(ys, prepend=ys[0])**2))
        ax_dist.plot(t, dists, linewidth=2, color=color, label=label)

    ax_xy.set_title('Simulated Trajectories')
    ax_xy.set_xlabel('x (m)')
    ax_xy.set_ylabel('y (m)')
    ax_xy.axis('equal')
    ax_xy.grid(True, alpha=0.3)
    ax_xy.legend(fontsize=8)

    ax_dist.set_title('Cumulative Distance Travelled')
    ax_dist.set_xlabel('Time (s)')
    ax_dist.set_ylabel('Distance (m)')
    ax_dist.grid(True, alpha=0.3)
    ax_dist.legend(fontsize=8)

    plt.tight_layout()
    out_path = os.path.expanduser('~/ros2_trajectory.png')
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    print(f'Plot saved -> {out_path}')


if __name__ == '__main__':
    main()
