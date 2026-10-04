"""E-bikes and NYC street safety — analysis of data/crashes.parquet"""
import duckdb, pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import Counter

P = './data/crashes.parquet'
OUT = './out/'
con = duckdb.connect()

df = con.sql(f'''
select collision_id, crash_date, crash_time, borough,
  number_of_persons_injured pi, number_of_persons_killed pk,
  number_of_pedestrians_injured ped_i, number_of_pedestrians_killed ped_k,
  number_of_cyclist_injured cyc_i, number_of_cyclist_killed cyc_k,
  number_of_motorist_injured mot_i, number_of_motorist_killed mot_k,
  list_value(coalesce(vehicle_type_code1,''),coalesce(vehicle_type_code2,''),coalesce(vehicle_type_code3,''),coalesce(vehicle_type_code4,''),coalesce(vehicle_type_code5,'')) vs,
  list_value(coalesce(contributing_factor_vehicle_1,''),coalesce(contributing_factor_vehicle_2,''),coalesce(contributing_factor_vehicle_3,''),coalesce(contributing_factor_vehicle_4,''),coalesce(contributing_factor_vehicle_5,'')) fs
from '{P}'
''').df()

def norm(v): return ' '.join(str(v).lower().replace('/', ' ').split())

def classify(v):
    v = norm(v)
    if not v: return None
    if 'e-bike' in v or 'e bike' in v or 'ebike' in v or v == 'electric b': return 'e-bike'
    if 'e-scooter' in v or 'e scooter' in v or 'escooter' in v or v == 'electric s': return 'e-scooter'
    if 'moped' in v: return 'moped'
    if 'scooter' in v: return 'scooter'
    if any(k in v for k in ['motorbike','minibike','dirt','motorcycle','motor cycle']): return 'motorcycle'
    if 'bicycl' in v or 'bike' in v or 'citibike' in v:
        return 'moped' if 'gas' in v else 'bicycle'
    return None

VEHCATS = ['e-bike','bicycle','e-scooter','moped','scooter','motorcycle']
df['cats'] = df['vs'].apply(lambda l: {c for c in map(classify, l) if c})
for c in VEHCATS:
    df['has_' + c] = df['cats'].apply(lambda s, c=c: c in s)
df['has_vru'] = df[['has_e-bike','has_bicycle','has_e-scooter','has_moped']].any(axis=1)
df['yr'] = pd.to_datetime(df['crash_date']).dt.year
df['hour'] = df['crash_time'].apply(lambda t: t.hour if hasattr(t,'hour') else int(t.total_seconds()//3600))
df['role_i'] = df.ped_i + df.cyc_i + df.mot_i
df['unattrib_i'] = df.pi - df.role_i          # injuries not attributed to ped/cyclist/motorist
df['unattrib_k'] = df.pk - (df.ped_k + df.cyc_k + df.mot_k)

W = df[df.yr.between(2016, 2025)].copy()      # analysis window (complete years)
E = W[W['has_e-bike']]
B = W[W['has_bicycle']]
S = W[W['has_e-scooter']]
N = W[~W['has_vru']]

def stats(s, name):
    n = len(s)
    return dict(group=name, crashes=n,
                inj_per_100=100*s.pi.sum()/n, k_per_1000=1000*s.pk.sum()/n,
                ped_inj_per_100=100*s.ped_i.sum()/n, ped_k_per_1000=1000*s.ped_k.sum()/n,
                cyc_inj_per_100=100*s.cyc_i.sum()/n,
                mot_inj_per_100=100*s.mot_i.sum()/n,
                unattrib_inj_per_100=100*s.unattrib_i.sum()/n,
                pct_any_inj=100*(s.pi>0).mean())
sev = pd.DataFrame([stats(E,'E-bike involved'), stats(B,'Bicycle involved'),
                    stats(S,'E-scooter involved'), stats(N,'No bike/scooter/moped'),
                    stats(W,'All crashes')])
print('\n=== SEVERITY PER CRASH, 2016-2025 ===')
print(sev.round(2).to_string(index=False))

print('\n=== ANNUAL ===')
g = W.groupby('yr').agg(crashes=('collision_id','size'), inj=('pi','sum'), killed=('pk','sum'),
    ped_inj=('ped_i','sum'), ped_k=('ped_k','sum'), cyc_inj=('cyc_i','sum'), cyc_k=('cyc_k','sum'),
    mot_inj=('mot_i','sum'), mot_k=('mot_k','sum'))
eb = E.groupby('yr').agg(eb_crashes=('collision_id','size'), eb_inj=('pi','sum'), eb_killed=('pk','sum'),
    eb_ped_inj=('ped_i','sum'), eb_ped_k=('ped_k','sum'), eb_cyc_inj=('cyc_i','sum'),
    eb_unattrib=('unattrib_i','sum'))
bi = B.groupby('yr').agg(bi_crashes=('collision_id','size'), bi_inj=('pi','sum'), bi_killed=('pk','sum'))
sp = S.groupby('yr').agg(sp_crashes=('collision_id','size'))
g = g.join(eb).join(bi).join(sp).fillna(0)
g['eb_share_pct'] = (100*g.eb_crashes/g.crashes).round(1)
g['eb_inj_share_pct'] = (100*g.eb_inj/g.inj).round(1)
g['eb_kill_share_pct'] = (100*g.eb_killed/g.killed).round(1)
g['eb_ped_inj_share_pct'] = (100*g.eb_ped_inj/g.ped_inj).round(1)
g['eb_cyc_inj_share_pct'] = (100*g.eb_cyc_inj/g.cyc_inj).round(1)
print(g[['crashes','eb_crashes','eb_share_pct','bi_crashes','sp_crashes','inj','killed',
         'eb_inj','eb_killed','eb_inj_share_pct','eb_kill_share_pct','eb_ped_inj_share_pct','eb_cyc_inj_share_pct']].to_string())

print('\n=== E-BIKE SHARE OF CUMULATIVE TOTALS 2021-2025 ===')
E5 = E[E.yr.between(2021,2025)]
W5 = W[W.yr.between(2021,2025)]
for lab, num, den in [('crashes', E5.pi.size, W5.pi.size),
                      ('injuries', E5.pi.sum(), W5.pi.sum()),
                      ('deaths', E5.pk.sum(), W5.pk.sum()),
                      ('ped injuries', E5.ped_i.sum(), W5.ped_i.sum()),
                      ('ped deaths', E5.ped_k.sum(), W5.ped_k.sum()),
                      ('cyclist injuries', E5.cyc_i.sum(), W5.cyc_i.sum()),
                      ('motorist injuries', E5.mot_i.sum(), W5.mot_i.sum())]:
    print(f'  {lab:20s} {num:7d} / {den:8d} = {100*num/den:5.1f}%')

print('\n=== CITYWIDE TREND (2016 vs 2025) ===')
print(g[['crashes','inj','killed','ped_inj','ped_k','cyc_inj','cyc_k','mot_inj','mot_k','eb_crashes','eb_inj','eb_killed']].loc[[2016,2019,2021,2023,2025]].to_string())

# unattributed-injury data quirk
print('\n=== UNATTRIBUTED INJURIES (person injured but not ped/cyclist/motorist) ===')
print(W.groupby('yr').apply(lambda s: pd.Series({
    'all_rows_mismatch': int((s.unattrib_i>0).sum()),
    'all_unattrib_inj': int(s.unattrib_i.sum()),
    'eb_rows_mismatch': int((s[s['has_e-bike']].unattrib_i>0).sum()),
    'eb_unattrib_inj': int(s[s['has_e-bike']].unattrib_i.sum()),
    'eb_total_inj': int(s[s['has_e-bike']].pi.sum())}), include_groups=False).to_string())

# --- key numbers
ur = E[E.unattrib_i > 0]
print(f"\n  unattributed rows: {len(ur)} of {len(E)} e-bike crashes; "
      f"{100*(ur.role_i==0).mean():.1f}% of them have all three role fields zero")
rider_rate = 100*(E.cyc_i + E.unattrib_i).sum()/len(E)
bike_rate = 100*B.cyc_i.sum()/len(B)
print(f"  rider-harm proxy (cyclist injured + unattributed) per 100 crashes: "
      f"e-bike {rider_rate:.1f} vs pedal bike {bike_rate:.1f}")
print(f"  e-bike crashes injuring at least one pedestrian: {100*(E.ped_i>0).mean():.1f}% "
      f"vs pedal bike {100*(B.ped_i>0).mean():.1f}%")
M = W[W['has_e-bike'] | W['has_e-scooter']]
W5b, M5 = W[W.yr >= 2021], M[M.yr >= 2021]
for lab, num, den in [('micromobility crashes', len(M5), len(W5b)),
                      ('micromobility injuries', M5.pi.sum(), W5b.pi.sum()),
                      ('micromobility deaths', M5.pk.sum(), W5b.pk.sum())]:
    print(f"  {lab} 2021-2025: {num} / {den} = {100*num/den:.1f}%")
print(f"  cyclist deaths in e-bike-involved crashes 2021-2025: {E[E.yr>=2021].cyc_k.sum()} / {W5b.cyc_k.sum()}")
print(f"  pedestrian deaths in e-bike-involved crashes 2021-2025: {E[E.yr>=2021].ped_k.sum()} / {W5b.ped_k.sum()}")

# hour of day
print('\n=== HOUR OF DAY (share of that group\'s crashes) ===')
hh = pd.DataFrame({
  'E-bike': E.hour.value_counts(normalize=True).sort_index(),
  'Bicycle': B.hour.value_counts(normalize=True).sort_index(),
  'All crashes': W.hour.value_counts(normalize=True).sort_index()}).fillna(0)*100
print(hh.round(1).to_string())
night = lambda s: 100*((s.hour>=20)|(s.hour<6)).mean()
print(f'night (20:00-05:59) share: e-bike {night(E):.1f}%  bicycle {night(B):.1f}%  all {night(W):.1f}%')
print(f'evening peak 17-19: e-bike {100*E.hour.between(17,19).mean():.1f}%  bicycle {100*B.hour.between(17,19).mean():.1f}%')

# factors
eb_f, bi_f = Counter(), Counter()
for vs, fs in zip(df.vs, df.fs):
    for v, f in zip(vs, fs):
        if classify(v) == 'e-bike' and f and f.strip(): eb_f[f.strip()] += 1
        if classify(v) == 'bicycle' and f and f.strip(): bi_f[f.strip()] += 1
def clean(c):
    return Counter({k2:v for k2,v in c.items() if k2.strip() and k2.strip().lower() != 'unspecified'})
eb_c, bi_c = clean(eb_f), clean(bi_f)
n_eb, n_bi = sum(eb_c.values()), sum(bi_c.values())
names = [k for k,_ in (eb_c + bi_c).most_common(10)]
facs = pd.DataFrame({'E-bike': {k: 100*eb_c.get(k,0)/n_eb for k in names},
                     'Bicycle': {k: 100*bi_c.get(k,0)/n_bi for k in names}})
print(f'\n=== TOP SPECIFIED CONTRIBUTING FACTORS (% of {n_eb} e-bike / {n_bi} bike factor entries) ===')
print(facs.round(1).to_string())

# borough
print('\n=== E-BIKE CRASH SHARE BY BOROUGH (2021-2025) ===')
bb = W5.groupby('borough').agg(crashes=('collision_id','size'), eb=('has_e-bike','sum'))
bb['eb_share_pct'] = (100*bb.eb/bb.crashes).round(1)
print(bb.sort_values('eb_share_pct', ascending=False).to_string())

# ---------------- CHARTS ----------------
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                     'figure.dpi': 130, 'axes.grid': True, 'grid.alpha': .25, 'grid.linestyle': ':'})
C_EB, C_BI, C_SP, C_ALL, C_N = '#d95f02', '#1b9e77', '#7570b3', '#8c8c8c', '#4c72b0'
yrs = list(range(2016, 2026))

# 1. trend
fig, ax = plt.subplots(1, 2, figsize=(12, 4.4))
ax[0].plot(yrs, g.bi_crashes, 'o-', color=C_BI, label='Bicycle (pedal)')
ax[0].plot(yrs, g.eb_crashes, 'o-', color=C_EB, label='E-bike')
ax[0].plot(yrs, g.sp_crashes, 'o-', color=C_SP, label='E-scooter')
ax[0].set_title('Crashes involving a micromobility vehicle')
ax[0].set_ylabel('crashes per year'); ax[0].set_xlabel('year'); ax[0].legend(frameon=False)
ax[1].bar(yrs, g.eb_share_pct, color=C_EB, label='E-bike share of all crashes')
ax[1].set_title('E-bikes as a share of all NYC crashes')
ax[1].set_ylabel('% of crashes'); ax[1].set_xlabel('year')
for x, v in zip(yrs, g.eb_share_pct):
    ax[1].text(x, v+0.1, f'{v:g}', ha='center', fontsize=8)
ax[1].set_ylim(0, max(g.eb_share_pct)*1.2)
fig.tight_layout(); fig.savefig(OUT+'01_ebike_crash_trend.png'); plt.close(fig)

# 2. severity per crash
fig, ax = plt.subplots(1, 2, figsize=(12, 4.4))
order = ['E-bike involved','Bicycle involved','E-scooter involved','No bike/scooter/moped','All crashes']
cols = [C_EB, C_BI, C_SP, C_N, C_ALL]
s2 = sev.set_index('group').loc[order]
ax[0].bar(range(len(order)), s2.inj_per_100, color=cols)
ax[0].set_xticks(range(len(order))); ax[0].set_xticklabels([o.replace(' involved','').replace('No bike/scooter/moped','Car/truck only') for o in order], rotation=20, ha='right')
ax[0].set_ylabel('people injured per 100 crashes'); ax[0].set_title('Injuries per crash')
for i, v in enumerate(s2.inj_per_100): ax[0].text(i, v+1.5, f'{v:.1f}', ha='center', fontsize=9)
ax[1].bar(range(len(order)), s2.k_per_1000, color=cols)
ax[1].set_xticks(range(len(order))); ax[1].set_xticklabels([o.replace(' involved','').replace('No bike/scooter/moped','Car/truck only') for o in order], rotation=20, ha='right')
ax[1].set_ylabel('people killed per 1,000 crashes'); ax[1].set_title('Fatalities per crash')
for i, v in enumerate(s2.k_per_1000): ax[1].text(i, v+0.15, f'{v:.1f}', ha='center', fontsize=9)
fig.suptitle('Severity per crash, 2016-2025 (crashes with vulnerable users are inherently more severe)',
             fontsize=10, y=1.0)
fig.tight_layout(); fig.savefig(OUT+'02_severity_per_crash.png'); plt.close(fig)

# 3. who gets hurt
fig, ax = plt.subplots(1, 3, figsize=(15, 4.4))
grp = {'E-bike': E, 'Bicycle': B, 'E-scooter': S, 'All crashes': W}
labels = ['Pedestrian','Cyclist','Motorist','Unattributed']
cl = ['#e7298a', '#1b9e77', '#4c72b0', '#bbbbbb']
left = np.zeros(len(grp))
for lab, c in zip(labels, cl):
    vals = []
    for k, s in grp.items():
        tot = s.pi.sum()
        vals.append({'Pedestrian': s.ped_i.sum(), 'Cyclist': s.cyc_i.sum(),
                     'Motorist': s.mot_i.sum(), 'Unattributed': s.unattrib_i.sum()}[lab]/tot*100)
    ax[0].barh(list(grp), vals, left=left, color=c, label=lab)
    left += np.array(vals)
ax[0].set_xlabel('% of people injured'); ax[0].set_title('Who gets hurt, 2016-2025')
ax[0].legend(frameon=False, fontsize=8, ncol=4, loc='upper center', bbox_to_anchor=(.5, -.18))
ax[0].set_xlim(0, 100)
for j, (ttl, key, fmt, dy) in enumerate([
        ('Pedestrians injured\nper 100 crashes', 'ped_inj_per_100', '{:.1f}', .2),
        ('Pedestrians killed\nper 1,000 crashes', 'ped_k_per_1000', '{:.2f}', .03)], start=1):
    v_eb, v_bi = s2.loc['E-bike involved', key], s2.loc['Bicycle involved', key]
    ax[j].bar([0, 1], [v_eb, v_bi], .5, color=[C_EB, C_BI])
    ax[j].set_xticks([0, 1]); ax[j].set_xticklabels(['E-bike', 'Bicycle'])
    ax[j].set_title(ttl); ax[j].set_xlim(-.6, 1.6)
    for xi, v, c in [(0, v_eb, C_EB), (1, v_bi, C_BI)]:
        ax[j].text(xi, v+dy, fmt.format(v), ha='center', fontsize=10, color=c)
fig.suptitle("Grey = injuries counted in \"persons injured\" but not coded as pedestrian/cyclist/motorist; "
             "these cluster in micromobility crashes (96% have all three role fields blank)",
             fontsize=9, y=0.99)
fig.tight_layout(rect=[0, 0, 1, 0.93]); fig.savefig(OUT+'03_who_is_hurt.png', bbox_inches='tight'); plt.close(fig)

# 4. citywide burden
fig, ax = plt.subplots(1, 2, figsize=(12, 4.4))
ax[0].bar(yrs, g.inj - g.eb_inj, color=C_ALL, label='all other crashes')
ax[0].bar(yrs, g.eb_inj, bottom=g.inj-g.eb_inj, color=C_EB, label='e-bike-involved')
ax[0].set_title('People injured per year, citywide'); ax[0].set_ylabel('injuries'); ax[0].legend(frameon=False, fontsize=8)
ax[0].set_ylim(0, g.inj.max()*1.15)
ax[1].bar(yrs, g.killed - g.eb_killed, color=C_ALL, label='all other crashes')
ax[1].bar(yrs, g.eb_killed, bottom=g.killed-g.eb_killed, color=C_EB, label='e-bike-involved')
ax[1].set_title('People killed per year, citywide'); ax[1].set_ylabel('deaths'); ax[1].legend(frameon=False, fontsize=8)
ax[1].set_ylim(0, g.killed.max()*1.25)
for i, (t, e) in enumerate(zip(g.inj, g.eb_inj)):
    if e: ax[0].text(yrs[i], t+700, f'{100*e/t:.1f}%', ha='center', fontsize=8, color=C_EB)
for i, (t, e) in enumerate(zip(g.killed, g.eb_killed)):
    if e: ax[1].text(yrs[i], t+8, f'{100*e/t:.1f}%', ha='center', fontsize=8, color=C_EB)
fig.suptitle('E-bike share of the citywide toll (label = % of that year\'s total from e-bike-involved crashes)', fontsize=10, y=1.0)
fig.tight_layout(); fig.savefig(OUT+'04_citywide_burden.png'); plt.close(fig)

# 5. hour of day
fig, ax = plt.subplots(figsize=(10, 4.2))
ax.plot(hh.index, hh['E-bike'], 'o-', color=C_EB, label='E-bike crashes')
ax.plot(hh.index, hh['Bicycle'], 'o-', color=C_BI, label='Bicycle crashes')
ax.plot(hh.index, hh['All crashes'], 'o--', color=C_ALL, label='All crashes')
ax.set_xticks(range(0, 24)); ax.set_xlabel('hour of day'); ax.set_ylabel('% of that group\'s crashes')
ax.set_title('When e-bike crashes happen: a night/delivery-time profile')
ax.legend(frameon=False); fig.tight_layout(); fig.savefig(OUT+'05_hour_of_day.png'); plt.close(fig)

# 6. factors
fig, ax = plt.subplots(figsize=(9, 4.6))
facs = facs.loc[facs.max(axis=1).sort_values(ascending=False).index]
yy = np.arange(len(facs))
ax.barh(yy-0.2, facs['E-bike'], .4, color=C_EB, label='E-bike')
ax.barh(yy+0.2, facs['Bicycle'], .4, color=C_BI, label='Bicycle')
ax.set_yticks(yy); ax.set_yticklabels(facs.index, fontsize=9)
ax.invert_yaxis(); ax.set_xlabel('% of specified factor entries'); ax.legend(frameon=False)
ax.set_title('Contributing factors recorded for the e-bike vs the pedal bike')
fig.tight_layout(); fig.savefig(OUT+'06_top_factors.png'); plt.close(fig)

print('\nSaved 6 charts to', OUT)
