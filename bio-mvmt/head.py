# smoothed velocity threshold algorithm
# savgol filtered velocities

def get_event_onset(vel_amp, start_idx):
    if start_idx <= 1:
        return np.nan

    # find preceeding local min
    temp_i = start_idx - 1
    while temp_i > 0:
        prev_val = vel_amp[temp_i - 1]
        this_val = vel_amp[temp_i]
        next_val = vel_amp[temp_i + 1]

        if prev_val >= this_val and this_val < next_val:
            return temp_i
        
        temp_i -= 1

    return np.nan

def get_event_offset(vel_amp, start_idx):
    if start_idx >= len(vel_amp) - 2:
        return np.nan

    temp_i = start_idx + 1
    # find following local min
    while temp_i < len(vel_amp) - 1:
        prev_val = vel_amp[temp_i - 1]
        this_val = vel_amp[temp_i]
        next_val = vel_amp[temp_i + 1]

        if prev_val >= this_val and this_val < next_val:
            return temp_i

        temp_i += 1
    
    return np.nan


def get_velocity_events(vel_mag, times, min_event_duration, max_event_duration, vel_thresh):
    # all points where velocity exceeds threshold
    idx_above_thresh = vel_mag >= vel_thresh
    
    diff_above_thresh = np.diff(idx_above_thresh.astype(int))
    idx_onset_initial = np.where(diff_above_thresh == 1)[0] + 1
    idx_offset_initial = np.where(diff_above_thresh == -1)[0] + 1

    # discard offsets before the first onset
    if len(idx_offset_initial) > 0 and (len(idx_onset_initial) == 0 or idx_offset_initial[0] < idx_onset_initial[0]):
        idx_offset_initial = idx_offset_initial[1:]
    # discard onset after the last offset
    if len(idx_onset_initial) > 0 and (len(idx_offset_initial) == 0 or idx_onset_initial[-1] > idx_offset_initial[-1]):
        idx_onset_initial = idx_onset_initial[:-1]

    if len(idx_onset_initial) == 0:
        return np.array([]), np.array([])

    # refine onsets and offsets, find local min
    event_onset_idx = []
    event_offset_idx = []
    
    for i in range(len(idx_onset_initial)):
        onset = get_event_onset(vel_mag, idx_onset_initial[i])
        offset = get_event_offset(vel_mag, idx_offset_initial[i])

        if not (np.isnan(onset) or np.isnan(offset)):
            onset = int(onset)
            offset = int(offset)
            duration = times[offset] - times[onset]
            if min_event_duration <= duration <= max_event_duration:
                event_onset_idx.append(onset)
                event_offset_idx.append(offset)
                
    return np.array(event_onset_idx), np.array(event_offset_idx)


def get_head_rotation_events(head_rot, time, cfg=None):
    if cfg is None:
        cfg = {
            'minEventDuration': 0.01,
            'velThresh': 30,
            'maxEventDuration': 3,
            'applySG': True,
            'sgLength': 0.2
        }

    if head_rot.shape[0] < head_rot.shape[1] and head_rot.shape[1] == 3:
        head_rot = head_rot.T
        
    head_vel = np.gradient(head_rot, time, axis=0)

    if cfg['applySG']:
        srate = 1.0 / np.mean(np.diff(time))
        sg_window = int(2 * np.floor((cfg['sgLength'] * srate) / 2) + 1)
        if sg_window > len(head_vel):
            sg_window = len(head_vel) - 1 if (len(head_vel) % 2 == 0) else len(head_vel)

        if sg_window > 2:
            head_vel = signal.savgol_filter(head_vel, window_length=sg_window, polyorder=2, axis=0)

    vel_mag = np.linalg.norm(head_vel, axis=1)

    rot_onset_idx, rot_offset_idx = get_velocity_events(
        vel_mag,
        time,
        cfg['minEventDuration'],
        cfg['maxEventDuration'],
        cfg['velThresh']
    )
    
    return rot_onset_idx, rot_offset_idx
