"""Seed the exercise library with ~200 built-in exercises.

Usage (inside Docker):
    python -m app.seed
"""

import asyncio

from sqlalchemy import func, select

from app.database import AsyncSessionLocal, engine  # noqa: F401
from app.models.exercise import EquipmentType, Exercise, MuscleGroup

# ---------------------------------------------------------------------------
# Exercise catalogue – 200 exercises across 11 muscle groups
# ---------------------------------------------------------------------------

EXERCISES: list[dict] = [
    # ── CHEST (23) ────────────────────────────────────────────────────────────
    {
        "name": "Barbell Bench Press",
        "primary_muscle": MuscleGroup.chest,
        "secondary_muscles": ["triceps", "shoulders"],
        "equipment": EquipmentType.barbell,
        "description": "A compound pressing movement and the gold-standard chest builder.",
        "instructions": (
            "1. Lie flat on a bench with feet firmly on the floor.\n"
            "2. Grip the bar slightly wider than shoulder-width.\n"
            "3. Unrack and lower the bar to mid-chest with elbows at ~45 degrees.\n"
            "4. Press the bar back up to full lockout.\n"
            "5. Keep your shoulder blades retracted throughout the movement."
        ),
    },
    {
        "name": "Incline Barbell Bench Press",
        "primary_muscle": MuscleGroup.chest,
        "secondary_muscles": ["triceps", "shoulders"],
        "equipment": EquipmentType.barbell,
        "description": "An incline pressing variation that emphasises the upper chest.",
        "instructions": (
            "1. Set the bench to a 30-45 degree incline.\n"
            "2. Grip the bar slightly wider than shoulder-width and unrack.\n"
            "3. Lower the bar to the upper chest just below the collarbone.\n"
            "4. Press up to lockout while keeping your back against the bench.\n"
            "5. Avoid flaring your elbows past 60 degrees."
        ),
    },
    {
        "name": "Decline Barbell Bench Press",
        "primary_muscle": MuscleGroup.chest,
        "secondary_muscles": ["triceps", "shoulders"],
        "equipment": EquipmentType.barbell,
        "description": "A decline pressing variation targeting the lower chest fibres.",
        "instructions": (
            "1. Set the bench to a 15-30 degree decline and secure your legs.\n"
            "2. Grip the bar slightly wider than shoulder-width.\n"
            "3. Unrack and lower the bar to the lower chest / sternum.\n"
            "4. Press the bar back up to lockout.\n"
            "5. Use a spotter or safety pins for heavy sets."
        ),
    },
    {
        "name": "Dumbbell Bench Press",
        "primary_muscle": MuscleGroup.chest,
        "secondary_muscles": ["triceps", "shoulders"],
        "equipment": EquipmentType.dumbbell,
        "description": "A dumbbell pressing movement allowing a greater range of motion than the barbell version.",
        "instructions": (
            "1. Sit on a flat bench holding a dumbbell in each hand on your thighs.\n"
            "2. Kick the weights up as you lie back, positioning them at chest level.\n"
            "3. Press the dumbbells up until your arms are extended, palms facing forward.\n"
            "4. Lower under control until your upper arms are parallel to the floor.\n"
            "5. Keep your feet flat and shoulder blades squeezed together."
        ),
    },
    {
        "name": "Incline Dumbbell Bench Press",
        "primary_muscle": MuscleGroup.chest,
        "secondary_muscles": ["triceps", "shoulders"],
        "equipment": EquipmentType.dumbbell,
        "description": "An incline dumbbell press that targets the upper chest with a full stretch.",
        "instructions": (
            "1. Set the bench to 30-45 degrees and sit back with a dumbbell in each hand.\n"
            "2. Press the dumbbells up over the upper chest.\n"
            "3. Lower until your elbows are at roughly 90 degrees.\n"
            "4. Drive the weights back up without clanging them together at the top.\n"
            "5. Maintain a slight arch in your lower back."
        ),
    },
    {
        "name": "Decline Dumbbell Bench Press",
        "primary_muscle": MuscleGroup.chest,
        "secondary_muscles": ["triceps", "shoulders"],
        "equipment": EquipmentType.dumbbell,
        "description": "A decline dumbbell press emphasising the lower chest with independent arm movement.",
        "instructions": (
            "1. Set the bench to a slight decline and secure your legs.\n"
            "2. Hold a dumbbell in each hand at chest level.\n"
            "3. Press the dumbbells upward until arms are fully extended.\n"
            "4. Lower slowly until elbows are at 90 degrees.\n"
            "5. Keep your core braced and back flat on the bench."
        ),
    },
    {
        "name": "Dumbbell Fly",
        "primary_muscle": MuscleGroup.chest,
        "secondary_muscles": ["shoulders"],
        "equipment": EquipmentType.dumbbell,
        "description": "An isolation movement that stretches and contracts the chest through a wide arc.",
        "instructions": (
            "1. Lie flat on a bench with a dumbbell in each hand, arms extended above your chest.\n"
            "2. With a slight bend in the elbows, lower the dumbbells out to the sides in a wide arc.\n"
            "3. Lower until you feel a deep stretch across the chest.\n"
            "4. Squeeze your pecs to bring the dumbbells back together.\n"
            "5. Keep the same elbow angle throughout; do not turn this into a press."
        ),
    },
    {
        "name": "Incline Dumbbell Fly",
        "primary_muscle": MuscleGroup.chest,
        "secondary_muscles": ["shoulders"],
        "equipment": EquipmentType.dumbbell,
        "description": "An incline fly variation emphasising the upper chest stretch.",
        "instructions": (
            "1. Set the bench to 30-45 degrees with a dumbbell in each hand.\n"
            "2. Start with arms extended above the upper chest, slight bend in the elbows.\n"
            "3. Lower the dumbbells outward in an arc until you feel a chest stretch.\n"
            "4. Reverse the motion by squeezing the upper pecs.\n"
            "5. Avoid going too heavy—control is more important than load."
        ),
    },
    {
        "name": "Cable Crossover",
        "primary_muscle": MuscleGroup.chest,
        "secondary_muscles": ["shoulders"],
        "equipment": EquipmentType.cable,
        "description": "A cable fly performed from high pulleys, providing constant tension on the chest.",
        "instructions": (
            "1. Set both cable pulleys to the highest position and attach D-handles.\n"
            "2. Stand centred between the cables with a slight forward lean.\n"
            "3. With a slight bend in the elbows, bring your hands together in front of your chest.\n"
            "4. Squeeze the pecs hard at the bottom, then slowly return to the start.\n"
            "5. Keep your torso stable and avoid rocking."
        ),
    },
    {
        "name": "Machine Chest Press",
        "primary_muscle": MuscleGroup.chest,
        "secondary_muscles": ["triceps", "shoulders"],
        "equipment": EquipmentType.machine,
        "description": "A machine-based pressing movement offering a guided, stable range of motion.",
        "instructions": (
            "1. Adjust the seat so the handles are at mid-chest height.\n"
            "2. Sit back firmly and grip the handles.\n"
            "3. Press the handles forward until your arms are extended.\n"
            "4. Return slowly until you feel a stretch in the chest.\n"
            "5. Avoid locking out aggressively at the top."
        ),
    },
    {
        "name": "Pec Deck Machine",
        "primary_muscle": MuscleGroup.chest,
        "secondary_muscles": ["shoulders"],
        "equipment": EquipmentType.machine,
        "description": "A machine fly that isolates the pecs through a fixed arc of motion.",
        "instructions": (
            "1. Adjust the seat height so your upper arms are parallel to the floor.\n"
            "2. Place your forearms against the pads or grip the handles.\n"
            "3. Squeeze your chest to bring the pads together in front of you.\n"
            "4. Hold the contraction briefly, then open back slowly.\n"
            "5. Do not let the weight stack slam between reps."
        ),
    },
    {
        "name": "Push-Up",
        "primary_muscle": MuscleGroup.chest,
        "secondary_muscles": ["triceps", "shoulders", "core"],
        "equipment": EquipmentType.bodyweight,
        "description": "The classic bodyweight push-up, a foundational upper-body exercise.",
        "instructions": (
            "1. Start in a high plank with hands slightly wider than shoulder-width.\n"
            "2. Brace your core so your body forms a straight line from head to heels.\n"
            "3. Lower your chest toward the floor by bending the elbows.\n"
            "4. Push back up to full arm extension.\n"
            "5. Avoid sagging your hips or flaring your elbows out wide."
        ),
    },
    {
        "name": "Diamond Push-Up",
        "primary_muscle": MuscleGroup.chest,
        "secondary_muscles": ["triceps", "shoulders"],
        "equipment": EquipmentType.bodyweight,
        "description": "A close-hand push-up variation that heavily recruits the inner chest and triceps.",
        "instructions": (
            "1. Place your hands together beneath your chest forming a diamond shape with your index fingers and thumbs.\n"
            "2. Extend your legs behind you into a plank position.\n"
            "3. Lower your chest to your hands, keeping elbows close to the body.\n"
            "4. Push back up to full lockout.\n"
            "5. Keep your core tight to prevent hip sag."
        ),
    },
    {
        "name": "Chest Dip",
        "primary_muscle": MuscleGroup.chest,
        "secondary_muscles": ["triceps", "shoulders"],
        "equipment": EquipmentType.bodyweight,
        "description": "A dip variation with a forward lean to shift emphasis onto the chest.",
        "instructions": (
            "1. Grip parallel dip bars and lift yourself to a locked-out position.\n"
            "2. Lean your torso forward about 30 degrees.\n"
            "3. Lower your body until your upper arms are parallel to the floor.\n"
            "4. Press back up by driving through the palms.\n"
            "5. Keep the forward lean consistent throughout the rep."
        ),
    },
    {
        "name": "Cable Fly (Low to High)",
        "primary_muscle": MuscleGroup.chest,
        "secondary_muscles": ["shoulders"],
        "equipment": EquipmentType.cable,
        "description": "A low-to-high cable fly that targets the upper chest fibres.",
        "instructions": (
            "1. Set both cable pulleys to the lowest position.\n"
            "2. Grip a handle in each hand and step forward into a staggered stance.\n"
            "3. With a slight bend in the elbows, sweep the handles upward and together at chin height.\n"
            "4. Squeeze the upper chest, then lower under control.\n"
            "5. Focus on the arc motion, not a pressing movement."
        ),
    },
    {
        "name": "Cable Fly (High to Low)",
        "primary_muscle": MuscleGroup.chest,
        "secondary_muscles": ["shoulders"],
        "equipment": EquipmentType.cable,
        "description": "A high-to-low cable fly emphasising the lower and inner chest.",
        "instructions": (
            "1. Set both cable pulleys to the highest position.\n"
            "2. Grip a handle in each hand and step forward.\n"
            "3. Bring the handles downward and together in front of your waist.\n"
            "4. Squeeze the lower chest at the bottom.\n"
            "5. Return slowly to the start position with arms wide."
        ),
    },
    {
        "name": "Landmine Press",
        "primary_muscle": MuscleGroup.chest,
        "secondary_muscles": ["shoulders", "triceps"],
        "equipment": EquipmentType.barbell,
        "description": "A standing press using one end of a barbell anchored on the floor, great for upper chest.",
        "instructions": (
            "1. Wedge one end of a barbell into a corner or landmine attachment.\n"
            "2. Hold the free end at chest height with both hands.\n"
            "3. Press the bar up and away from your body at a ~45-degree angle.\n"
            "4. Lower the bar back to your chest under control.\n"
            "5. Keep your core braced and avoid excessive back extension."
        ),
    },
    {
        "name": "Floor Press",
        "primary_muscle": MuscleGroup.chest,
        "secondary_muscles": ["triceps", "shoulders"],
        "equipment": EquipmentType.barbell,
        "description": "A bench press performed on the floor, limiting range of motion to build lockout strength.",
        "instructions": (
            "1. Lie on the floor under a barbell in a rack or have a partner hand it to you.\n"
            "2. Grip the bar at bench-press width.\n"
            "3. Lower the bar until your upper arms touch the floor.\n"
            "4. Pause briefly, then press back up to lockout.\n"
            "5. Keep your legs flat or with bent knees — avoid using leg drive."
        ),
    },
    {
        "name": "Svend Press",
        "primary_muscle": MuscleGroup.chest,
        "secondary_muscles": ["shoulders"],
        "equipment": EquipmentType.other,
        "description": "A plate squeeze press that creates constant tension through the inner chest.",
        "instructions": (
            "1. Stand upright holding two small plates pressed together at chest height.\n"
            "2. Squeeze the plates hard with your palms.\n"
            "3. Extend your arms forward while maintaining the squeeze.\n"
            "4. Bring the plates back to your chest.\n"
            "5. Focus on squeezing the chest throughout the entire range of motion."
        ),
    },
    {
        "name": "Machine Incline Press",
        "primary_muscle": MuscleGroup.chest,
        "secondary_muscles": ["triceps", "shoulders"],
        "equipment": EquipmentType.machine,
        "description": "An incline press performed on a machine, ideal for safely targeting the upper chest.",
        "instructions": (
            "1. Adjust the seat so the handles align with your upper chest.\n"
            "2. Sit back and grip the handles firmly.\n"
            "3. Press forward and upward until your arms are extended.\n"
            "4. Lower the weight slowly until you feel a stretch in the upper chest.\n"
            "5. Keep your back flat against the pad throughout."
        ),
    },
    {
        "name": "Wide-Grip Push-Up",
        "primary_muscle": MuscleGroup.chest,
        "secondary_muscles": ["shoulders", "triceps"],
        "equipment": EquipmentType.bodyweight,
        "description": "A push-up with a wider hand placement to increase chest activation.",
        "instructions": (
            "1. Set up in a plank position with hands placed wider than shoulder-width.\n"
            "2. Keep your body in a straight line from head to heels.\n"
            "3. Lower your chest toward the ground, flaring elbows to about 60-70 degrees.\n"
            "4. Push back up to the start position.\n"
            "5. Avoid letting your lower back sag."
        ),
    },
    {
        "name": "Decline Dumbbell Fly",
        "primary_muscle": MuscleGroup.chest,
        "secondary_muscles": ["shoulders"],
        "equipment": EquipmentType.dumbbell,
        "description": "A decline fly that stretches and contracts the lower portion of the pecs.",
        "instructions": (
            "1. Set the bench to a slight decline and secure your legs.\n"
            "2. Hold a dumbbell in each hand with arms extended above your chest.\n"
            "3. Lower the dumbbells out to the sides in a wide arc with a slight elbow bend.\n"
            "4. Squeeze your lower chest to bring the weights back together.\n"
            "5. Use a controlled tempo — do not bounce at the bottom."
        ),
    },
    {
        "name": "Squeeze Press",
        "primary_muscle": MuscleGroup.chest,
        "secondary_muscles": ["triceps"],
        "equipment": EquipmentType.dumbbell,
        "description": "A dumbbell press where the weights are squeezed together to maximise inner-chest activation.",
        "instructions": (
            "1. Lie flat on a bench with a dumbbell in each hand.\n"
            "2. Press the dumbbells together at arm's length above your chest.\n"
            "3. Keep the dumbbells touching and press inward throughout the movement.\n"
            "4. Lower to your chest while maintaining inward pressure.\n"
            "5. Press back up, squeezing the dumbbells together the entire time."
        ),
    },
    # ── BACK (24) ─────────────────────────────────────────────────────────────
    {
        "name": "Barbell Row",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["biceps", "forearms", "core"],
        "equipment": EquipmentType.barbell,
        "description": "A bent-over barbell row, one of the most effective mass-building back exercises.",
        "instructions": (
            "1. Stand with feet shoulder-width apart, hinge at the hips until your torso is roughly 45 degrees.\n"
            "2. Grip the bar slightly wider than shoulder-width with an overhand grip.\n"
            "3. Pull the bar toward your lower ribcage, driving the elbows back.\n"
            "4. Squeeze your shoulder blades together at the top.\n"
            "5. Lower the bar under control and repeat."
        ),
    },
    {
        "name": "Pendlay Row",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["biceps", "forearms", "core"],
        "equipment": EquipmentType.barbell,
        "description": "A strict bent-over row where the bar returns to the floor each rep for maximum power.",
        "instructions": (
            "1. Stand over the bar with feet shoulder-width apart, torso nearly parallel to the floor.\n"
            "2. Grip the bar with an overhand grip at shoulder width.\n"
            "3. Explosively row the bar to your lower chest.\n"
            "4. Lower the bar back to the floor and let it settle before the next rep.\n"
            "5. Keep your back flat and avoid using momentum from the hips."
        ),
    },
    {
        "name": "Dumbbell Row",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["biceps", "forearms"],
        "equipment": EquipmentType.dumbbell,
        "description": "A single-arm dumbbell row that builds lat thickness and corrects imbalances.",
        "instructions": (
            "1. Place one knee and hand on a bench, keeping your back flat.\n"
            "2. Hold a dumbbell in the opposite hand with your arm extended.\n"
            "3. Row the dumbbell toward your hip, driving the elbow past your torso.\n"
            "4. Squeeze your lat at the top, then lower under control.\n"
            "5. Complete all reps on one side before switching."
        ),
    },
    {
        "name": "Pull-Up",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["biceps", "forearms", "core"],
        "equipment": EquipmentType.bodyweight,
        "description": "An overhand-grip vertical pull, the king of bodyweight back exercises.",
        "instructions": (
            "1. Hang from a pull-up bar with an overhand grip, hands slightly wider than shoulders.\n"
            "2. Engage your lats and pull yourself up until your chin clears the bar.\n"
            "3. Pause briefly at the top.\n"
            "4. Lower yourself under control to a full dead hang.\n"
            "5. Avoid kipping or swinging your legs."
        ),
    },
    {
        "name": "Chin-Up",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["biceps", "forearms"],
        "equipment": EquipmentType.bodyweight,
        "description": "An underhand-grip pull-up that heavily recruits the biceps alongside the lats.",
        "instructions": (
            "1. Hang from a bar with a supinated (underhand) grip at shoulder-width.\n"
            "2. Pull yourself up until your chin is above the bar.\n"
            "3. Focus on driving your elbows down and back.\n"
            "4. Lower yourself slowly to a full hang.\n"
            "5. Keep your core tight to prevent swinging."
        ),
    },
    {
        "name": "Lat Pulldown (Wide Grip)",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["biceps", "forearms"],
        "equipment": EquipmentType.cable,
        "description": "A wide-grip cable pulldown that develops lat width.",
        "instructions": (
            "1. Sit at a lat pulldown station and grip the bar wider than shoulder-width.\n"
            "2. Lean back slightly and pull the bar down to your upper chest.\n"
            "3. Squeeze your lats at the bottom of the movement.\n"
            "4. Extend your arms slowly to return the bar overhead.\n"
            "5. Avoid pulling behind the neck — keep it in front."
        ),
    },
    {
        "name": "Lat Pulldown (Close Grip)",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["biceps", "forearms"],
        "equipment": EquipmentType.cable,
        "description": "A close-grip pulldown that shifts focus to the lower lats and mid-back.",
        "instructions": (
            "1. Attach a V-bar or close-grip handle to the lat pulldown cable.\n"
            "2. Sit down and grip the handle with a neutral or supinated grip.\n"
            "3. Pull the handle toward your sternum, leaning back slightly.\n"
            "4. Squeeze your lats at the bottom and slowly return to the top.\n"
            "5. Keep your elbows tucked close to your body."
        ),
    },
    {
        "name": "Seated Cable Row",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["biceps", "forearms"],
        "equipment": EquipmentType.cable,
        "description": "A horizontal cable row building mid-back thickness.",
        "instructions": (
            "1. Sit at a cable row station with your feet on the platform and knees slightly bent.\n"
            "2. Grip the V-bar or wide handle and sit upright.\n"
            "3. Pull the handle toward your abdomen, driving your elbows back.\n"
            "4. Squeeze your shoulder blades together at full contraction.\n"
            "5. Extend your arms forward under control without rounding your back."
        ),
    },
    {
        "name": "T-Bar Row",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["biceps", "forearms", "core"],
        "equipment": EquipmentType.barbell,
        "description": "A barbell row using a landmine or T-bar apparatus for thick mid-back development.",
        "instructions": (
            "1. Straddle a loaded barbell anchored at one end or use a T-bar machine.\n"
            "2. Hinge at the hips and grip the handle or bar.\n"
            "3. Row the weight toward your chest, keeping your back flat.\n"
            "4. Squeeze your back at the top, then lower under control.\n"
            "5. Avoid rounding your lower back — brace your core throughout."
        ),
    },
    {
        "name": "Deadlift",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["hamstrings", "glutes", "forearms", "core"],
        "equipment": EquipmentType.barbell,
        "description": "The conventional deadlift, a full-body pull and one of the most effective strength exercises.",
        "instructions": (
            "1. Stand with feet hip-width apart, the bar over mid-foot.\n"
            "2. Hinge at the hips and grip the bar just outside your knees.\n"
            "3. Flatten your back, brace your core, and drive through the floor.\n"
            "4. Stand up by extending your hips and knees simultaneously.\n"
            "5. Lower the bar by hinging at the hips first, then bending the knees."
        ),
    },
    {
        "name": "Rack Pull",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["hamstrings", "glutes", "forearms"],
        "equipment": EquipmentType.barbell,
        "description": "A partial deadlift from pins or blocks that targets the upper back and lockout strength.",
        "instructions": (
            "1. Set the safety pins in a power rack to just below knee height.\n"
            "2. Stand over the bar and grip it with a shoulder-width or mixed grip.\n"
            "3. Brace your core and pull the bar to a standing position.\n"
            "4. Squeeze your traps and upper back at lockout.\n"
            "5. Lower the bar back to the pins in a controlled manner."
        ),
    },
    {
        "name": "Straight-Arm Pulldown",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["core", "triceps"],
        "equipment": EquipmentType.cable,
        "description": "An isolation cable exercise for the lats performed with straight arms.",
        "instructions": (
            "1. Attach a straight bar or rope to a high cable pulley.\n"
            "2. Stand facing the machine with a slight forward lean.\n"
            "3. With arms nearly straight, pull the handle down toward your thighs.\n"
            "4. Squeeze your lats at the bottom, then slowly return overhead.\n"
            "5. Keep a slight bend in the elbows to protect the joints."
        ),
    },
    {
        "name": "Cable Pullover",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["chest", "triceps"],
        "equipment": EquipmentType.cable,
        "description": "A cable pullover that trains the lats through a long range of motion under constant tension.",
        "instructions": (
            "1. Attach a straight bar to a high cable pulley.\n"
            "2. Kneel or stand a few feet from the machine, gripping the bar overhead.\n"
            "3. Pull the bar downward in an arc until your hands reach hip level.\n"
            "4. Squeeze your lats, then reverse the arc slowly.\n"
            "5. Keep your arms relatively straight throughout."
        ),
    },
    {
        "name": "Machine Row",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["biceps"],
        "equipment": EquipmentType.machine,
        "description": "A plate-loaded or selectorized rowing machine for controlled back training.",
        "instructions": (
            "1. Adjust the chest pad so your arms can fully extend.\n"
            "2. Grip the handles and sit firmly against the pad.\n"
            "3. Row the handles toward your torso, squeezing your shoulder blades.\n"
            "4. Return slowly to the starting position.\n"
            "5. Keep your chest against the pad — do not lean back."
        ),
    },
    {
        "name": "Inverted Row",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["biceps", "core"],
        "equipment": EquipmentType.bodyweight,
        "description": "A bodyweight horizontal row performed under a bar or with suspension straps.",
        "instructions": (
            "1. Set a barbell in a rack at about waist height or grab suspension handles.\n"
            "2. Hang beneath the bar with arms extended, body straight.\n"
            "3. Pull your chest to the bar by driving your elbows back.\n"
            "4. Squeeze your back at the top, then lower yourself under control.\n"
            "5. Keep your body rigid like a reverse plank."
        ),
    },
    {
        "name": "Meadows Row",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["biceps", "forearms"],
        "equipment": EquipmentType.barbell,
        "description": "A single-arm landmine row developed by John Meadows for lat and upper-back detail.",
        "instructions": (
            "1. Stand perpendicular to a barbell in a landmine setup.\n"
            "2. Stagger your feet and hinge forward at the hips.\n"
            "3. Grip the end of the bar with an overhand grip.\n"
            "4. Row the bar toward your hip, driving the elbow up and back.\n"
            "5. Lower with control, letting the lat stretch at the bottom."
        ),
    },
    {
        "name": "Chest-Supported Dumbbell Row",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["biceps"],
        "equipment": EquipmentType.dumbbell,
        "description": "A row performed face-down on an incline bench, eliminating momentum.",
        "instructions": (
            "1. Set an incline bench to about 30-45 degrees.\n"
            "2. Lie face-down with a dumbbell in each hand, arms hanging straight.\n"
            "3. Row both dumbbells toward your hips simultaneously.\n"
            "4. Squeeze the shoulder blades together at the top.\n"
            "5. Lower slowly — the bench support prevents cheating."
        ),
    },
    {
        "name": "Dumbbell Pullover",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["chest", "triceps"],
        "equipment": EquipmentType.dumbbell,
        "description": "A pullover movement stretching the lats and serratus under load.",
        "instructions": (
            "1. Lie across a flat bench with only your upper back supported.\n"
            "2. Hold one dumbbell overhead with both hands, arms slightly bent.\n"
            "3. Lower the dumbbell behind your head in an arc until you feel a deep lat stretch.\n"
            "4. Pull the dumbbell back overhead by contracting the lats.\n"
            "5. Keep your hips slightly lower than the bench for a better stretch."
        ),
    },
    {
        "name": "Hyperextension",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["hamstrings", "glutes"],
        "equipment": EquipmentType.bodyweight,
        "description": "A back extension on a hyperextension bench strengthening the spinal erectors.",
        "instructions": (
            "1. Position yourself on a hyperextension bench with hips at the edge of the pad.\n"
            "2. Cross your arms over your chest or behind your head.\n"
            "3. Lower your torso toward the floor by hinging at the hips.\n"
            "4. Raise your torso back up until your body forms a straight line.\n"
            "5. Avoid hyperextending past neutral — stop at a flat back."
        ),
    },
    {
        "name": "Seal Row",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["biceps"],
        "equipment": EquipmentType.dumbbell,
        "description": "A strict chest-supported row performed lying face-down on a raised bench to eliminate momentum.",
        "instructions": (
            "1. Lie face-down on a bench elevated on blocks so your arms can hang freely.\n"
            "2. Hold a dumbbell in each hand with arms fully extended.\n"
            "3. Row both dumbbells up toward your ribcage.\n"
            "4. Squeeze your back at the top, then lower slowly.\n"
            "5. Keep your chest flat against the bench — no body English."
        ),
    },
    {
        "name": "Single-Arm Cable Row",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["biceps", "core"],
        "equipment": EquipmentType.cable,
        "description": "A unilateral cable row that builds the lats and challenges core stability.",
        "instructions": (
            "1. Attach a D-handle to a cable set at navel height.\n"
            "2. Stand or kneel facing the machine and grip the handle.\n"
            "3. Row the handle toward your hip, rotating your torso slightly.\n"
            "4. Squeeze the lat, then return the handle with control.\n"
            "5. Complete all reps on one side before switching."
        ),
    },
    {
        "name": "Barbell Pullover",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["chest", "triceps"],
        "equipment": EquipmentType.barbell,
        "description": "A pullover using a barbell for lat and serratus development.",
        "instructions": (
            "1. Lie flat on a bench holding an EZ-bar or straight bar with a narrow grip.\n"
            "2. Start with the bar over your chest, arms slightly bent.\n"
            "3. Lower the bar behind your head in an arc until your upper arms are in line with your ears.\n"
            "4. Pull the bar back to the starting position using your lats.\n"
            "5. Keep your core braced and lower back pressed into the bench."
        ),
    },
    {
        "name": "Snatch-Grip Deadlift",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["hamstrings", "glutes", "shoulders", "forearms"],
        "equipment": EquipmentType.barbell,
        "description": "A deadlift with a wide snatch grip that increases upper-back and trap recruitment.",
        "instructions": (
            "1. Stand with feet hip-width apart and grip the bar with a very wide overhand grip.\n"
            "2. Set your back flat and hips lower than a conventional deadlift.\n"
            "3. Drive through the floor to stand up, keeping the bar close.\n"
            "4. Lock out at the top with your traps engaged.\n"
            "5. Lower with control, maintaining the wide grip throughout."
        ),
    },
    {
        "name": "Neutral-Grip Lat Pulldown",
        "primary_muscle": MuscleGroup.back,
        "secondary_muscles": ["biceps", "forearms"],
        "equipment": EquipmentType.cable,
        "description": "A lat pulldown with palms facing each other, balancing lat and bicep recruitment.",
        "instructions": (
            "1. Attach a neutral-grip handle to the lat pulldown cable.\n"
            "2. Sit down and grip the handles with palms facing each other.\n"
            "3. Pull the handle down to your upper chest.\n"
            "4. Squeeze your lats, then slowly extend your arms.\n"
            "5. Keep your torso upright with a slight lean back."
        ),
    },
    # ── SHOULDERS (23) ────────────────────────────────────────────────────────
    {
        "name": "Overhead Press (Barbell)",
        "primary_muscle": MuscleGroup.shoulders,
        "secondary_muscles": ["triceps", "core"],
        "equipment": EquipmentType.barbell,
        "description": "The standing barbell overhead press, a foundational shoulder and upper-body strength exercise.",
        "instructions": (
            "1. Unrack a barbell at shoulder height, gripping slightly wider than shoulder-width.\n"
            "2. Brace your core and press the bar straight overhead.\n"
            "3. Lock out with the bar over your mid-foot and head pushed slightly forward.\n"
            "4. Lower the bar back to the front of your shoulders under control.\n"
            "5. Avoid excessive back lean — squeeze your glutes for stability."
        ),
    },
    {
        "name": "Seated Dumbbell Press",
        "primary_muscle": MuscleGroup.shoulders,
        "secondary_muscles": ["triceps"],
        "equipment": EquipmentType.dumbbell,
        "description": "A seated overhead press with dumbbells allowing independent arm movement.",
        "instructions": (
            "1. Sit on a bench set to 90 degrees with a dumbbell in each hand at shoulder height.\n"
            "2. Press both dumbbells overhead until arms are extended.\n"
            "3. Lower the dumbbells to shoulder level with elbows at roughly 90 degrees.\n"
            "4. Keep your back flat against the pad.\n"
            "5. Avoid clanging the dumbbells together at the top."
        ),
    },
    {
        "name": "Arnold Press",
        "primary_muscle": MuscleGroup.shoulders,
        "secondary_muscles": ["triceps", "chest"],
        "equipment": EquipmentType.dumbbell,
        "description": "A rotating dumbbell press that hits all three deltoid heads in one movement.",
        "instructions": (
            "1. Sit with dumbbells at shoulder height, palms facing you.\n"
            "2. As you press up, rotate your wrists so palms face forward at the top.\n"
            "3. Lock out overhead, then reverse the rotation as you lower.\n"
            "4. Finish with palms facing you at the bottom.\n"
            "5. Use a smooth, continuous rotation throughout the rep."
        ),
    },
    {
        "name": "Lateral Raise",
        "primary_muscle": MuscleGroup.shoulders,
        "secondary_muscles": [],
        "equipment": EquipmentType.dumbbell,
        "description": "An isolation exercise for the lateral deltoid, building shoulder width.",
        "instructions": (
            "1. Stand with a dumbbell in each hand at your sides.\n"
            "2. Raise your arms out to the sides until they reach shoulder height.\n"
            "3. Lead with your elbows and keep a slight bend in the arm.\n"
            "4. Pause at the top, then lower under control.\n"
            "5. Avoid swinging or using body momentum."
        ),
    },
    {
        "name": "Cable Lateral Raise",
        "primary_muscle": MuscleGroup.shoulders,
        "secondary_muscles": [],
        "equipment": EquipmentType.cable,
        "description": "A lateral raise on a cable, providing constant tension through the full range of motion.",
        "instructions": (
            "1. Set a cable pulley to the lowest position with a D-handle.\n"
            "2. Stand sideways to the machine and grip the handle with the far hand.\n"
            "3. Raise your arm out to the side until parallel with the floor.\n"
            "4. Lower slowly, maintaining tension on the delt.\n"
            "5. Complete all reps on one side, then switch."
        ),
    },
    {
        "name": "Front Raise",
        "primary_muscle": MuscleGroup.shoulders,
        "secondary_muscles": ["chest"],
        "equipment": EquipmentType.dumbbell,
        "description": "An isolation movement targeting the anterior (front) deltoid.",
        "instructions": (
            "1. Stand holding dumbbells in front of your thighs with palms facing you.\n"
            "2. Raise one or both arms in front of you to shoulder height.\n"
            "3. Keep your elbows slightly bent and avoid swinging.\n"
            "4. Lower under control.\n"
            "5. Alternate arms or lift both simultaneously."
        ),
    },
    {
        "name": "Rear Delt Fly (Dumbbell)",
        "primary_muscle": MuscleGroup.shoulders,
        "secondary_muscles": ["back"],
        "equipment": EquipmentType.dumbbell,
        "description": "A bent-over fly isolating the posterior deltoids.",
        "instructions": (
            "1. Hinge at the hips with a flat back, a dumbbell in each hand.\n"
            "2. With a slight elbow bend, raise the dumbbells out to the sides.\n"
            "3. Squeeze the rear delts at the top of the movement.\n"
            "4. Lower slowly back to the starting position.\n"
            "5. Keep your torso angle consistent — do not stand up during the rep."
        ),
    },
    {
        "name": "Reverse Pec Deck",
        "primary_muscle": MuscleGroup.shoulders,
        "secondary_muscles": ["back"],
        "equipment": EquipmentType.machine,
        "description": "A machine fly performed in reverse to target the rear deltoids.",
        "instructions": (
            "1. Sit facing the pad on a pec deck machine, gripping the handles.\n"
            "2. Open your arms outward in a reverse fly motion.\n"
            "3. Squeeze the rear delts at full contraction.\n"
            "4. Return slowly to the starting position.\n"
            "5. Adjust the seat so your arms move in line with your shoulders."
        ),
    },
    {
        "name": "Cable Rear Delt Fly",
        "primary_muscle": MuscleGroup.shoulders,
        "secondary_muscles": ["back"],
        "equipment": EquipmentType.cable,
        "description": "A cable fly for the rear delts, providing constant tension throughout the rep.",
        "instructions": (
            "1. Set two cables at roughly shoulder height without handles.\n"
            "2. Cross-grip the cables (left cable in right hand and vice versa).\n"
            "3. Pull your arms apart in a reverse fly, squeezing the rear delts.\n"
            "4. Return slowly to the crossed position.\n"
            "5. Keep your arms at shoulder height throughout."
        ),
    },
    {
        "name": "Upright Row",
        "primary_muscle": MuscleGroup.shoulders,
        "secondary_muscles": ["biceps"],
        "equipment": EquipmentType.barbell,
        "description": "A pulling movement from waist to chin that trains the lateral delts and traps.",
        "instructions": (
            "1. Stand holding a barbell with a shoulder-width or slightly narrower grip.\n"
            "2. Pull the bar straight up along your body toward your chin.\n"
            "3. Lead with the elbows, keeping them higher than your hands.\n"
            "4. Lower the bar under control.\n"
            "5. Avoid pulling higher than your collarbone to protect the shoulder joint."
        ),
    },
    {
        "name": "Barbell Shrug",
        "primary_muscle": MuscleGroup.shoulders,
        "secondary_muscles": ["forearms"],
        "equipment": EquipmentType.barbell,
        "description": "A barbell shrug for building the upper trapezius muscles.",
        "instructions": (
            "1. Stand holding a barbell in front of you with arms extended.\n"
            "2. Shrug your shoulders straight up toward your ears.\n"
            "3. Hold the contraction at the top for one second.\n"
            "4. Lower your shoulders slowly.\n"
            "5. Avoid rolling your shoulders — shrug straight up and down."
        ),
    },
    {
        "name": "Dumbbell Shrug",
        "primary_muscle": MuscleGroup.shoulders,
        "secondary_muscles": ["forearms"],
        "equipment": EquipmentType.dumbbell,
        "description": "A dumbbell shrug offering a more natural hand position for trap development.",
        "instructions": (
            "1. Stand with a dumbbell in each hand at your sides, palms facing your body.\n"
            "2. Shrug your shoulders upward as high as possible.\n"
            "3. Squeeze the traps at the top.\n"
            "4. Lower under control.\n"
            "5. Keep your arms straight throughout — do not bend the elbows."
        ),
    },
    {
        "name": "Face Pull",
        "primary_muscle": MuscleGroup.shoulders,
        "secondary_muscles": ["back"],
        "equipment": EquipmentType.cable,
        "description": "A cable pull targeting the rear delts and rotator cuff for shoulder health.",
        "instructions": (
            "1. Set a cable with a rope attachment at upper-chest height.\n"
            "2. Grip the rope with both hands, palms facing in.\n"
            "3. Pull the rope toward your face, flaring your elbows high.\n"
            "4. Externally rotate your hands at the end so your fists point to the ceiling.\n"
            "5. Return slowly and keep your upper arms parallel to the floor."
        ),
    },
    {
        "name": "Landmine Press (Single Arm)",
        "primary_muscle": MuscleGroup.shoulders,
        "secondary_muscles": ["chest", "triceps", "core"],
        "equipment": EquipmentType.barbell,
        "description": "A unilateral pressing movement using a landmine for shoulder and core stability.",
        "instructions": (
            "1. Wedge one end of a barbell into a landmine and load the other end.\n"
            "2. Stand with a staggered stance and hold the bar end in one hand at shoulder height.\n"
            "3. Press the bar up and away from your body.\n"
            "4. Lower back to the shoulder with control.\n"
            "5. Keep your core tight to resist rotation."
        ),
    },
    {
        "name": "Machine Shoulder Press",
        "primary_muscle": MuscleGroup.shoulders,
        "secondary_muscles": ["triceps"],
        "equipment": EquipmentType.machine,
        "description": "A machine overhead press providing a safe, guided path for shoulder development.",
        "instructions": (
            "1. Adjust the seat so the handles start at shoulder height.\n"
            "2. Grip the handles and sit firmly against the back pad.\n"
            "3. Press the handles overhead to full extension.\n"
            "4. Lower until your elbows are at 90 degrees.\n"
            "5. Keep your back flat against the pad throughout."
        ),
    },
    {
        "name": "Pike Push-Up",
        "primary_muscle": MuscleGroup.shoulders,
        "secondary_muscles": ["triceps", "core"],
        "equipment": EquipmentType.bodyweight,
        "description": "A bodyweight overhead pressing movement that mimics a vertical press.",
        "instructions": (
            "1. Start in a downward-dog position with hips high and hands shoulder-width apart.\n"
            "2. Bend your elbows and lower your head toward the floor.\n"
            "3. Push back up to the starting position.\n"
            "4. Keep your legs as straight as possible.\n"
            "5. The closer your feet are to your hands, the more vertical the press becomes."
        ),
    },
    {
        "name": "Plate Front Raise",
        "primary_muscle": MuscleGroup.shoulders,
        "secondary_muscles": ["chest"],
        "equipment": EquipmentType.other,
        "description": "A front raise using a weight plate for constant grip engagement.",
        "instructions": (
            "1. Stand holding a weight plate at hip level with both hands at 9-and-3 o'clock.\n"
            "2. Raise the plate in front of you until your arms are parallel to the floor.\n"
            "3. Hold briefly at the top.\n"
            "4. Lower the plate back to hip level under control.\n"
            "5. Keep your torso upright — avoid leaning back."
        ),
    },
    {
        "name": "Band Pull-Apart",
        "primary_muscle": MuscleGroup.shoulders,
        "secondary_muscles": ["back"],
        "equipment": EquipmentType.band,
        "description": "A resistance band exercise for rear delts and scapular retraction.",
        "instructions": (
            "1. Hold a resistance band in front of you at shoulder height with straight arms.\n"
            "2. Pull the band apart by moving your hands outward.\n"
            "3. Squeeze your rear delts and upper back at full stretch.\n"
            "4. Return to the starting position with control.\n"
            "5. Keep your arms at shoulder height throughout."
        ),
    },
    {
        "name": "Z-Press",
        "primary_muscle": MuscleGroup.shoulders,
        "secondary_muscles": ["triceps", "core"],
        "equipment": EquipmentType.barbell,
        "description": "A seated-on-the-floor overhead press that demands strict form and core engagement.",
        "instructions": (
            "1. Sit on the floor inside a power rack with legs extended in front of you.\n"
            "2. Unrack the barbell at shoulder height.\n"
            "3. Press the bar overhead to lockout.\n"
            "4. Lower back to shoulder height.\n"
            "5. Without back support, your core must work hard to stabilise the lift."
        ),
    },
    {
        "name": "Cable Front Raise",
        "primary_muscle": MuscleGroup.shoulders,
        "secondary_muscles": ["chest"],
        "equipment": EquipmentType.cable,
        "description": "A front raise using a low cable for continuous tension on the anterior delt.",
        "instructions": (
            "1. Stand facing away from a low cable pulley with a D-handle in one hand.\n"
            "2. Raise your arm in front of you to shoulder height.\n"
            "3. Lower slowly, keeping tension on the front delt.\n"
            "4. Complete all reps then switch arms.\n"
            "5. Keep a slight bend in the elbow throughout."
        ),
    },
    {
        "name": "Handstand Push-Up",
        "primary_muscle": MuscleGroup.shoulders,
        "secondary_muscles": ["triceps", "core"],
        "equipment": EquipmentType.bodyweight,
        "description": "An advanced bodyweight overhead press performed in a handstand position.",
        "instructions": (
            "1. Kick up into a handstand against a wall with arms fully extended.\n"
            "2. Lower yourself by bending your elbows until your head gently touches the floor.\n"
            "3. Press back up to full lockout.\n"
            "4. Keep your core tight and body in a straight line.\n"
            "5. Use an ab-mat or pad under your head for safety."
        ),
    },
    {
        "name": "Seated Lateral Raise",
        "primary_muscle": MuscleGroup.shoulders,
        "secondary_muscles": [],
        "equipment": EquipmentType.dumbbell,
        "description": "A lateral raise performed while seated to eliminate momentum and isolate the delts.",
        "instructions": (
            "1. Sit on the edge of a bench with a dumbbell in each hand at your sides.\n"
            "2. Raise both arms out to the sides until they reach shoulder height.\n"
            "3. Pause briefly at the top.\n"
            "4. Lower the weights slowly.\n"
            "5. Seated position prevents any cheating with the legs or hips."
        ),
    },
    {
        "name": "Cuban Press",
        "primary_muscle": MuscleGroup.shoulders,
        "secondary_muscles": ["back"],
        "equipment": EquipmentType.dumbbell,
        "description": "A multi-phase movement combining an upright row, external rotation, and press for rotator cuff health.",
        "instructions": (
            "1. Stand with light dumbbells, arms at your sides.\n"
            "2. Perform an upright row, bringing elbows to shoulder height.\n"
            "3. Externally rotate the dumbbells until your forearms point to the ceiling.\n"
            "4. Press the dumbbells overhead.\n"
            "5. Reverse the sequence to return to the start. Use light weight."
        ),
    },
    # ── BICEPS (18) ───────────────────────────────────────────────────────────
    {
        "name": "Barbell Curl",
        "primary_muscle": MuscleGroup.biceps,
        "secondary_muscles": ["forearms"],
        "equipment": EquipmentType.barbell,
        "description": "The standard barbell curl, a staple for building overall bicep mass.",
        "instructions": (
            "1. Stand with feet shoulder-width apart, holding a barbell with an underhand grip.\n"
            "2. Curl the bar up toward your shoulders by flexing at the elbows.\n"
            "3. Squeeze the biceps at the top.\n"
            "4. Lower the bar under control to full arm extension.\n"
            "5. Keep your elbows pinned at your sides — do not swing."
        ),
    },
    {
        "name": "EZ-Bar Curl",
        "primary_muscle": MuscleGroup.biceps,
        "secondary_muscles": ["forearms"],
        "equipment": EquipmentType.barbell,
        "description": "A curl using an EZ-bar to reduce wrist strain while targeting the biceps.",
        "instructions": (
            "1. Stand holding an EZ-bar on the inner or outer angled grips.\n"
            "2. Curl the bar upward, keeping your upper arms stationary.\n"
            "3. Squeeze at the top.\n"
            "4. Lower slowly to full extension.\n"
            "5. The angled grip is easier on the wrists than a straight bar."
        ),
    },
    {
        "name": "Dumbbell Curl",
        "primary_muscle": MuscleGroup.biceps,
        "secondary_muscles": ["forearms"],
        "equipment": EquipmentType.dumbbell,
        "description": "A classic dumbbell curl performed alternating or simultaneously.",
        "instructions": (
            "1. Stand with a dumbbell in each hand, arms at your sides, palms forward.\n"
            "2. Curl one or both dumbbells toward your shoulders.\n"
            "3. Squeeze the bicep at the top.\n"
            "4. Lower under control.\n"
            "5. Keep your torso still — avoid rocking back and forth."
        ),
    },
    {
        "name": "Hammer Curl",
        "primary_muscle": MuscleGroup.biceps,
        "secondary_muscles": ["forearms"],
        "equipment": EquipmentType.dumbbell,
        "description": "A neutral-grip curl that targets the brachialis and brachioradialis alongside the biceps.",
        "instructions": (
            "1. Stand holding dumbbells with a neutral grip (palms facing each other).\n"
            "2. Curl the weights up without rotating your wrists.\n"
            "3. Squeeze at the top.\n"
            "4. Lower slowly.\n"
            "5. This grip is excellent for building arm thickness."
        ),
    },
    {
        "name": "Incline Dumbbell Curl",
        "primary_muscle": MuscleGroup.biceps,
        "secondary_muscles": ["forearms"],
        "equipment": EquipmentType.dumbbell,
        "description": "A curl on an incline bench that places the bicep in a stretched position for a deeper contraction.",
        "instructions": (
            "1. Set a bench to a 45-degree incline and sit back with a dumbbell in each hand.\n"
            "2. Let your arms hang straight down.\n"
            "3. Curl the dumbbells up without moving your upper arms forward.\n"
            "4. Squeeze at the top, then lower to full stretch.\n"
            "5. The incline prevents cheating and increases the range of motion."
        ),
    },
    {
        "name": "Preacher Curl (Barbell)",
        "primary_muscle": MuscleGroup.biceps,
        "secondary_muscles": ["forearms"],
        "equipment": EquipmentType.barbell,
        "description": "A curl on a preacher bench that isolates the biceps by bracing the upper arms.",
        "instructions": (
            "1. Sit at a preacher bench and rest your upper arms on the pad.\n"
            "2. Grip a barbell or EZ-bar with an underhand grip.\n"
            "3. Curl the bar up toward your chin.\n"
            "4. Lower slowly until your arms are nearly fully extended.\n"
            "5. Do not let the weight drop quickly at the bottom — control the eccentric."
        ),
    },
    {
        "name": "Preacher Curl (Dumbbell)",
        "primary_muscle": MuscleGroup.biceps,
        "secondary_muscles": ["forearms"],
        "equipment": EquipmentType.dumbbell,
        "description": "A single-arm preacher curl allowing focused unilateral bicep training.",
        "instructions": (
            "1. Sit at a preacher bench and drape one arm over the pad.\n"
            "2. Hold a dumbbell with an underhand grip.\n"
            "3. Curl the dumbbell upward, keeping your upper arm pressed into the pad.\n"
            "4. Lower slowly to near-full extension.\n"
            "5. Complete all reps, then switch arms."
        ),
    },
    {
        "name": "Concentration Curl",
        "primary_muscle": MuscleGroup.biceps,
        "secondary_muscles": [],
        "equipment": EquipmentType.dumbbell,
        "description": "A seated single-arm curl that maximises bicep peak contraction.",
        "instructions": (
            "1. Sit on a bench with legs apart, holding a dumbbell in one hand.\n"
            "2. Brace the back of your working arm against your inner thigh.\n"
            "3. Curl the dumbbell up toward your shoulder.\n"
            "4. Squeeze hard at the top, then lower slowly.\n"
            "5. Only your forearm should move — your upper arm stays stationary."
        ),
    },
    {
        "name": "Cable Curl",
        "primary_muscle": MuscleGroup.biceps,
        "secondary_muscles": ["forearms"],
        "equipment": EquipmentType.cable,
        "description": "A curl using a low cable to maintain constant tension on the biceps.",
        "instructions": (
            "1. Attach a straight bar or EZ-bar to a low cable pulley.\n"
            "2. Stand facing the machine and grip the bar underhand.\n"
            "3. Curl the bar up toward your shoulders.\n"
            "4. Squeeze, then lower with control.\n"
            "5. Keep your elbows by your sides throughout."
        ),
    },
    {
        "name": "Cable Hammer Curl",
        "primary_muscle": MuscleGroup.biceps,
        "secondary_muscles": ["forearms"],
        "equipment": EquipmentType.cable,
        "description": "A neutral-grip cable curl targeting the brachialis and outer bicep.",
        "instructions": (
            "1. Attach a rope handle to a low cable pulley.\n"
            "2. Grip the rope with a neutral (hammer) grip.\n"
            "3. Curl the rope upward, keeping elbows at your sides.\n"
            "4. Squeeze at the top, then lower under control.\n"
            "5. The cable provides tension even at the bottom of the rep."
        ),
    },
    {
        "name": "Spider Curl",
        "primary_muscle": MuscleGroup.biceps,
        "secondary_muscles": ["forearms"],
        "equipment": EquipmentType.dumbbell,
        "description": "A curl performed face-down on an incline bench for a strong peak contraction.",
        "instructions": (
            "1. Lie face-down on an incline bench set to about 45 degrees.\n"
            "2. Let your arms hang straight down with a dumbbell in each hand.\n"
            "3. Curl the dumbbells up, keeping your upper arms perpendicular to the floor.\n"
            "4. Squeeze at the top, then lower slowly.\n"
            "5. Gravity works against you hardest at the top, making the peak contraction intense."
        ),
    },
    {
        "name": "Reverse Curl",
        "primary_muscle": MuscleGroup.biceps,
        "secondary_muscles": ["forearms"],
        "equipment": EquipmentType.barbell,
        "description": "A curl with an overhand grip that develops the brachioradialis and forearm extensors.",
        "instructions": (
            "1. Stand holding a barbell with a pronated (overhand) grip.\n"
            "2. Curl the bar upward, keeping your wrists straight.\n"
            "3. Squeeze at the top.\n"
            "4. Lower under control.\n"
            "5. Use a lighter weight than standard curls — your grip is the limiting factor."
        ),
    },
    {
        "name": "Drag Curl",
        "primary_muscle": MuscleGroup.biceps,
        "secondary_muscles": ["forearms"],
        "equipment": EquipmentType.barbell,
        "description": "A curl where the bar stays close to the body and elbows move back, emphasising the long head.",
        "instructions": (
            "1. Stand holding a barbell with an underhand grip.\n"
            "2. Curl the bar upward while pulling your elbows back behind your body.\n"
            "3. The bar should drag up along your torso.\n"
            "4. Squeeze the bicep, then lower the bar along the same path.\n"
            "5. This shifts emphasis to the outer (long) head of the bicep."
        ),
    },
    {
        "name": "Machine Curl",
        "primary_muscle": MuscleGroup.biceps,
        "secondary_muscles": ["forearms"],
        "equipment": EquipmentType.machine,
        "description": "A machine-based bicep curl offering a fixed path and consistent resistance.",
        "instructions": (
            "1. Adjust the seat so your upper arms rest flat on the pad.\n"
            "2. Grip the handles with an underhand grip.\n"
            "3. Curl the handles toward your shoulders.\n"
            "4. Squeeze, then lower under control.\n"
            "5. Avoid lifting your elbows off the pad."
        ),
    },
    {
        "name": "Bayesian Curl",
        "primary_muscle": MuscleGroup.biceps,
        "secondary_muscles": [],
        "equipment": EquipmentType.cable,
        "description": "A cable curl performed facing away from the machine for maximum long-head stretch.",
        "instructions": (
            "1. Attach a D-handle to a low cable and face away from the machine.\n"
            "2. Grip the handle with one hand and step forward so your arm is pulled behind you.\n"
            "3. Curl the handle forward and up, keeping your elbow behind your body.\n"
            "4. Squeeze at the top and lower slowly.\n"
            "5. The stretched position makes this exceptional for the long head."
        ),
    },
    {
        "name": "Zottman Curl",
        "primary_muscle": MuscleGroup.biceps,
        "secondary_muscles": ["forearms"],
        "equipment": EquipmentType.dumbbell,
        "description": "A curl that combines a supinated curl on the way up with a pronated (reverse) lower for forearm work.",
        "instructions": (
            "1. Stand with a dumbbell in each hand, palms facing forward.\n"
            "2. Curl the dumbbells up with a supinated grip.\n"
            "3. At the top, rotate your wrists to a pronated (palms-down) position.\n"
            "4. Lower the dumbbells slowly with the overhand grip.\n"
            "5. Rotate back to supinated at the bottom and repeat."
        ),
    },
    {
        "name": "Cross-Body Hammer Curl",
        "primary_muscle": MuscleGroup.biceps,
        "secondary_muscles": ["forearms"],
        "equipment": EquipmentType.dumbbell,
        "description": "A hammer curl where the dumbbell travels across the body, targeting the brachialis.",
        "instructions": (
            "1. Stand holding a dumbbell in one hand at your side, neutral grip.\n"
            "2. Curl the dumbbell across your body toward the opposite shoulder.\n"
            "3. Squeeze at the top, then lower to the starting position.\n"
            "4. Alternate arms each rep or complete one side first.\n"
            "5. Keep your elbow stationary — only the forearm should move."
        ),
    },
    {
        "name": "Overhead Cable Curl",
        "primary_muscle": MuscleGroup.biceps,
        "secondary_muscles": [],
        "equipment": EquipmentType.cable,
        "description": "A cable curl with arms held wide and high to mimic a front double-bicep pose.",
        "instructions": (
            "1. Stand between two high cable pulleys and grip the D-handles.\n"
            "2. Hold your upper arms parallel to the floor, elbows at shoulder height.\n"
            "3. Curl the handles toward your head by flexing the biceps.\n"
            "4. Squeeze hard, then slowly extend your arms back out.\n"
            "5. Keep your upper arms fixed in position throughout."
        ),
    },
    # ── TRICEPS (14) ──────────────────────────────────────────────────────────
    {
        "name": "Tricep Pushdown (Cable)",
        "primary_muscle": MuscleGroup.triceps,
        "secondary_muscles": [],
        "equipment": EquipmentType.cable,
        "description": "A fundamental cable isolation movement for the triceps using a bar attachment.",
        "instructions": (
            "1. Attach a straight bar or V-bar to a high cable pulley.\n"
            "2. Stand facing the machine with elbows pinned at your sides.\n"
            "3. Push the bar downward until your arms are fully extended.\n"
            "4. Squeeze the triceps at lockout.\n"
            "5. Return slowly to the starting position — do not let the weight stack slam."
        ),
    },
    {
        "name": "Overhead Tricep Extension (Cable)",
        "primary_muscle": MuscleGroup.triceps,
        "secondary_muscles": ["shoulders"],
        "equipment": EquipmentType.cable,
        "description": "A cable overhead extension using a rope to stretch and load the long head of the tricep.",
        "instructions": (
            "1. Attach a rope to a low cable pulley.\n"
            "2. Face away from the machine, holding the rope behind your head.\n"
            "3. Step forward and lean slightly, keeping elbows close to your ears.\n"
            "4. Extend your arms overhead until they are fully straight.\n"
            "5. Lower the rope behind your head slowly, feeling the stretch in the long head."
        ),
    },
    {
        "name": "Skull Crusher (Barbell)",
        "primary_muscle": MuscleGroup.triceps,
        "secondary_muscles": ["shoulders", "chest"],
        "equipment": EquipmentType.barbell,
        "description": "A lying tricep extension that loads all three heads of the triceps.",
        "instructions": (
            "1. Lie on a flat bench holding a barbell or EZ-bar with arms extended overhead.\n"
            "2. Keeping your upper arms vertical, bend at the elbows to lower the bar toward your forehead.\n"
            "3. Stop just above your forehead (or behind your head for more stretch).\n"
            "4. Extend your arms back to the starting position.\n"
            "5. Keep your elbows from flaring outward."
        ),
    },
    {
        "name": "Skull Crusher (Dumbbell)",
        "primary_muscle": MuscleGroup.triceps,
        "secondary_muscles": ["shoulders"],
        "equipment": EquipmentType.dumbbell,
        "description": "A lying tricep extension with dumbbells allowing neutral-grip and independent arm work.",
        "instructions": (
            "1. Lie on a flat bench with a dumbbell in each hand, arms extended overhead.\n"
            "2. With palms facing each other, bend the elbows to lower the dumbbells beside your head.\n"
            "3. Keep your upper arms still.\n"
            "4. Extend back up to lockout, squeezing the triceps.\n"
            "5. The neutral grip reduces elbow stress compared to a barbell."
        ),
    },
    {
        "name": "Close-Grip Bench Press",
        "primary_muscle": MuscleGroup.triceps,
        "secondary_muscles": ["chest", "shoulders"],
        "equipment": EquipmentType.barbell,
        "description": "A bench press with a narrow grip that shifts emphasis from the chest to the triceps.",
        "instructions": (
            "1. Lie on a flat bench and grip the bar at shoulder-width or slightly narrower.\n"
            "2. Unrack the bar and lower it to your lower chest with elbows tucked at your sides.\n"
            "3. Press the bar up to full lockout.\n"
            "4. Focus on using the triceps to drive the movement.\n"
            "5. Do not grip too narrow — shoulder-width is sufficient."
        ),
    },
    {
        "name": "Dumbbell Kickback",
        "primary_muscle": MuscleGroup.triceps,
        "secondary_muscles": [],
        "equipment": EquipmentType.dumbbell,
        "description": "An isolation movement targeting the triceps through full elbow extension.",
        "instructions": (
            "1. Hinge forward at the hips and hold a dumbbell in one hand.\n"
            "2. Pin your upper arm parallel to the floor, elbow bent at 90 degrees.\n"
            "3. Extend your forearm backward until your arm is fully straight.\n"
            "4. Squeeze the tricep at lockout, then lower slowly.\n"
            "5. Keep your upper arm completely still throughout."
        ),
    },
    {
        "name": "Overhead Dumbbell Extension",
        "primary_muscle": MuscleGroup.triceps,
        "secondary_muscles": ["shoulders"],
        "equipment": EquipmentType.dumbbell,
        "description": "A seated or standing overhead extension with a dumbbell, stretching the long head of the triceps.",
        "instructions": (
            "1. Hold a single dumbbell overhead with both hands wrapped around one end.\n"
            "2. Keep your upper arms close to your ears.\n"
            "3. Lower the dumbbell behind your head by bending at the elbows.\n"
            "4. Extend back up to lockout.\n"
            "5. Keep your core braced to avoid arching your back."
        ),
    },
    {
        "name": "Dip (Tricep-focused)",
        "primary_muscle": MuscleGroup.triceps,
        "secondary_muscles": ["chest", "shoulders"],
        "equipment": EquipmentType.bodyweight,
        "description": "A dip performed with an upright torso to maximise tricep activation.",
        "instructions": (
            "1. Grip parallel dip bars and lift yourself to lockout.\n"
            "2. Keep your torso as vertical as possible.\n"
            "3. Lower yourself until your elbows reach about 90 degrees.\n"
            "4. Press back up to full lockout, focusing on the triceps.\n"
            "5. Keeping upright shifts the emphasis from the chest to the triceps."
        ),
    },
    {
        "name": "Cable Overhead Extension",
        "primary_muscle": MuscleGroup.triceps,
        "secondary_muscles": [],
        "equipment": EquipmentType.cable,
        "description": "A single-arm overhead cable extension isolating one tricep at a time.",
        "instructions": (
            "1. Attach a D-handle to a low cable pulley.\n"
            "2. Face away from the machine and hold the handle behind your head.\n"
            "3. Extend your arm overhead until fully straight.\n"
            "4. Lower the handle behind your head under control.\n"
            "5. Complete all reps on one arm, then switch."
        ),
    },
    {
        "name": "JM Press",
        "primary_muscle": MuscleGroup.triceps,
        "secondary_muscles": ["chest", "shoulders"],
        "equipment": EquipmentType.barbell,
        "description": "A hybrid of a close-grip bench press and skull crusher, targeting the triceps with heavy loads.",
        "instructions": (
            "1. Lie on a flat bench and grip the bar at shoulder-width.\n"
            "2. Unrack the bar over your upper chest.\n"
            "3. Lower the bar by bending the elbows and bringing it toward your chin/upper chest.\n"
            "4. The bar path is a blend between a press and a skull crusher.\n"
            "5. Press back to lockout — use a spotter as this is a technical lift."
        ),
    },
    {
        "name": "Tricep Machine Dip",
        "primary_muscle": MuscleGroup.triceps,
        "secondary_muscles": ["chest", "shoulders"],
        "equipment": EquipmentType.machine,
        "description": "A machine-based dip that provides consistent resistance for the triceps.",
        "instructions": (
            "1. Sit in the dip machine and adjust the seat height.\n"
            "2. Grip the handles at your sides.\n"
            "3. Press the handles downward until your arms are extended.\n"
            "4. Return slowly to the starting position.\n"
            "5. Adjust the weight to maintain full range of motion."
        ),
    },
    {
        "name": "Bench Dip",
        "primary_muscle": MuscleGroup.triceps,
        "secondary_muscles": ["chest", "shoulders"],
        "equipment": EquipmentType.bodyweight,
        "description": "A bodyweight dip using a bench behind you, great for beginners.",
        "instructions": (
            "1. Place your hands on the edge of a bench behind you, fingers forward.\n"
            "2. Extend your legs out in front of you (bend knees to make it easier).\n"
            "3. Lower your body by bending the elbows until they reach about 90 degrees.\n"
            "4. Press back up to full arm extension.\n"
            "5. Keep your back close to the bench throughout."
        ),
    },
    {
        "name": "Tate Press",
        "primary_muscle": MuscleGroup.triceps,
        "secondary_muscles": ["chest"],
        "equipment": EquipmentType.dumbbell,
        "description": "A dumbbell pressing variation where the elbows flare out to isolate the triceps.",
        "instructions": (
            "1. Lie on a flat bench with a dumbbell in each hand, pressed to lockout.\n"
            "2. Point your elbows outward and lower the dumbbells by bending the elbows.\n"
            "3. Bring the dumbbell ends down toward your chest.\n"
            "4. Press back up to lockout by extending the elbows.\n"
            "5. Use moderate weight — this is an isolation exercise."
        ),
    },
    {
        "name": "Single-Arm Tricep Pushdown",
        "primary_muscle": MuscleGroup.triceps,
        "secondary_muscles": [],
        "equipment": EquipmentType.cable,
        "description": "A unilateral cable pushdown to correct tricep imbalances.",
        "instructions": (
            "1. Attach a D-handle to a high cable pulley.\n"
            "2. Face the machine and grip the handle with one hand.\n"
            "3. Pin your elbow at your side and push the handle down to full extension.\n"
            "4. Squeeze the tricep, then return under control.\n"
            "5. Complete all reps, then switch arms."
        ),
    },
    # ── FOREARMS (9) ──────────────────────────────────────────────────────────
    {
        "name": "Wrist Curl (Barbell)",
        "primary_muscle": MuscleGroup.forearms,
        "secondary_muscles": [],
        "equipment": EquipmentType.barbell,
        "description": "A wrist flexion exercise that builds the forearm flexors.",
        "instructions": (
            "1. Sit on a bench and rest your forearms on your thighs, wrists hanging over the edge.\n"
            "2. Hold a barbell with an underhand grip.\n"
            "3. Let the bar roll down to your fingertips.\n"
            "4. Curl your wrists upward, squeezing the forearms.\n"
            "5. Lower slowly and repeat."
        ),
    },
    {
        "name": "Reverse Wrist Curl",
        "primary_muscle": MuscleGroup.forearms,
        "secondary_muscles": [],
        "equipment": EquipmentType.barbell,
        "description": "A wrist extension exercise targeting the forearm extensors.",
        "instructions": (
            "1. Sit on a bench with forearms on your thighs, wrists hanging over the edge.\n"
            "2. Hold a barbell with an overhand (pronated) grip.\n"
            "3. Extend your wrists upward as high as possible.\n"
            "4. Lower slowly to the starting position.\n"
            "5. Use lighter weight than regular wrist curls — the extensors are smaller."
        ),
    },
    {
        "name": "Farmer's Walk",
        "primary_muscle": MuscleGroup.forearms,
        "secondary_muscles": ["core", "shoulders"],
        "equipment": EquipmentType.dumbbell,
        "description": "A loaded carry that develops grip strength, core stability, and overall conditioning.",
        "instructions": (
            "1. Pick up a heavy dumbbell or farmer's walk handle in each hand.\n"
            "2. Stand tall with shoulders back and core braced.\n"
            "3. Walk forward with controlled, even steps.\n"
            "4. Continue for a set distance or time.\n"
            "5. Maintain an upright posture — do not let the weight pull you forward."
        ),
    },
    {
        "name": "Dead Hang",
        "primary_muscle": MuscleGroup.forearms,
        "secondary_muscles": ["back", "shoulders"],
        "equipment": EquipmentType.bodyweight,
        "description": "A static hang from a pull-up bar to build grip endurance and decompress the spine.",
        "instructions": (
            "1. Grip a pull-up bar with an overhand grip at shoulder-width.\n"
            "2. Hang with arms fully extended and feet off the ground.\n"
            "3. Engage your shoulders slightly — do not let them jam into your ears.\n"
            "4. Hold for as long as possible.\n"
            "5. Focus on even breathing throughout the hold."
        ),
    },
    {
        "name": "Plate Pinch",
        "primary_muscle": MuscleGroup.forearms,
        "secondary_muscles": [],
        "equipment": EquipmentType.other,
        "description": "A grip exercise where you pinch weight plates together to build thumb and finger strength.",
        "instructions": (
            "1. Place two smooth-sided weight plates together.\n"
            "2. Pinch them between your thumb and fingers.\n"
            "3. Lift them off the ground and hold for time.\n"
            "4. Set them down and repeat with the other hand.\n"
            "5. Start light — even small plates are challenging."
        ),
    },
    {
        "name": "Wrist Roller",
        "primary_muscle": MuscleGroup.forearms,
        "secondary_muscles": [],
        "equipment": EquipmentType.other,
        "description": "A forearm exercise using a roller device to wind a weight up and down.",
        "instructions": (
            "1. Hold a wrist roller at arm's length with a weight hanging from the cord.\n"
            "2. Roll the handle forward with alternating wrist movements to raise the weight.\n"
            "3. Once fully wound, reverse to lower the weight slowly.\n"
            "4. Keep your arms extended throughout.\n"
            "5. One full roll-up-and-down cycle is one set."
        ),
    },
    {
        "name": "Wrist Curl (Dumbbell)",
        "primary_muscle": MuscleGroup.forearms,
        "secondary_muscles": [],
        "equipment": EquipmentType.dumbbell,
        "description": "A single-arm wrist curl with a dumbbell for focused forearm flexor work.",
        "instructions": (
            "1. Sit on a bench, resting your forearm on your thigh with your wrist over the knee.\n"
            "2. Hold a dumbbell with an underhand grip.\n"
            "3. Curl your wrist upward, squeezing the forearm.\n"
            "4. Lower slowly.\n"
            "5. Complete all reps then switch arms."
        ),
    },
    {
        "name": "Behind-the-Back Barbell Wrist Curl",
        "primary_muscle": MuscleGroup.forearms,
        "secondary_muscles": [],
        "equipment": EquipmentType.barbell,
        "description": "A standing wrist curl with the bar behind your back, allowing heavier loading.",
        "instructions": (
            "1. Stand holding a barbell behind your back with a palms-back grip.\n"
            "2. Let the bar roll to your fingertips.\n"
            "3. Curl your wrists and fingers to roll the bar back up.\n"
            "4. Squeeze the forearms at the top.\n"
            "5. This standing variation allows you to handle more weight than seated versions."
        ),
    },
    {
        "name": "Towel Hang",
        "primary_muscle": MuscleGroup.forearms,
        "secondary_muscles": ["back", "shoulders"],
        "equipment": EquipmentType.bodyweight,
        "description": "A dead hang performed gripping towels for advanced grip and forearm training.",
        "instructions": (
            "1. Drape two towels over a pull-up bar.\n"
            "2. Grip one towel in each hand.\n"
            "3. Hang with full arm extension and feet off the ground.\n"
            "4. Hold for as long as possible.\n"
            "5. The thick, unstable grip makes this much harder than a regular dead hang."
        ),
    },
    # ── CORE (26) ─────────────────────────────────────────────────────────────
    {
        "name": "Plank",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": ["shoulders"],
        "equipment": EquipmentType.bodyweight,
        "description": "An isometric hold that builds core endurance and stabilisation.",
        "instructions": (
            "1. Start in a forearm plank with elbows under shoulders.\n"
            "2. Keep your body in a straight line from head to heels.\n"
            "3. Brace your core and squeeze your glutes.\n"
            "4. Hold the position without letting your hips sag or pike up.\n"
            "5. Breathe steadily and hold for the desired duration."
        ),
    },
    {
        "name": "Side Plank",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": ["shoulders", "glutes"],
        "equipment": EquipmentType.bodyweight,
        "description": "A lateral isometric hold targeting the obliques and lateral core stabilisers.",
        "instructions": (
            "1. Lie on your side with your elbow directly beneath your shoulder.\n"
            "2. Lift your hips off the ground, forming a straight line from head to feet.\n"
            "3. Stack your feet or stagger them for more stability.\n"
            "4. Hold the position, keeping your hips from dropping.\n"
            "5. Complete the hold, then switch sides."
        ),
    },
    {
        "name": "Crunch",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": [],
        "equipment": EquipmentType.bodyweight,
        "description": "A basic abdominal crunch isolating the upper rectus abdominis.",
        "instructions": (
            "1. Lie on your back with knees bent and feet flat on the floor.\n"
            "2. Place your hands behind your head or across your chest.\n"
            "3. Curl your shoulders off the floor by contracting your abs.\n"
            "4. Pause at the top, then lower slowly.\n"
            "5. Avoid pulling on your neck — the movement comes from the abs."
        ),
    },
    {
        "name": "Bicycle Crunch",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": [],
        "equipment": EquipmentType.bodyweight,
        "description": "A dynamic crunch combining rotation and leg movement for the obliques and rectus abdominis.",
        "instructions": (
            "1. Lie on your back with hands behind your head, legs raised with knees bent.\n"
            "2. Bring your right elbow toward your left knee while extending the right leg.\n"
            "3. Alternate sides in a pedalling motion.\n"
            "4. Rotate through your torso — do not just move your elbows.\n"
            "5. Keep your lower back pressed into the floor."
        ),
    },
    {
        "name": "Russian Twist",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": [],
        "equipment": EquipmentType.bodyweight,
        "description": "A seated rotational exercise targeting the obliques.",
        "instructions": (
            "1. Sit on the floor with knees bent, feet flat or elevated.\n"
            "2. Lean back slightly so your torso is at about 45 degrees.\n"
            "3. Clasp your hands together (or hold a weight) and twist your torso side to side.\n"
            "4. Touch the floor on each side.\n"
            "5. Move with control — speed is less important than range of rotation."
        ),
    },
    {
        "name": "Hanging Leg Raise",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": ["forearms"],
        "equipment": EquipmentType.bodyweight,
        "description": "An advanced core exercise performed hanging from a bar, targeting the lower abs.",
        "instructions": (
            "1. Hang from a pull-up bar with arms fully extended.\n"
            "2. With legs straight, raise them until they are parallel to the floor (or higher).\n"
            "3. Pause at the top, then lower slowly.\n"
            "4. Avoid swinging — initiate the movement from your abs.\n"
            "5. Bend your knees slightly if straight legs are too difficult."
        ),
    },
    {
        "name": "Hanging Knee Raise",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": ["forearms"],
        "equipment": EquipmentType.bodyweight,
        "description": "A more accessible version of the hanging leg raise, targeting the lower abs.",
        "instructions": (
            "1. Hang from a pull-up bar with arms extended.\n"
            "2. Bend your knees and raise them toward your chest.\n"
            "3. Curl your pelvis up slightly to maximise abdominal engagement.\n"
            "4. Lower your legs slowly back to the hanging position.\n"
            "5. Avoid excessive swinging."
        ),
    },
    {
        "name": "Cable Woodchop",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": ["shoulders"],
        "equipment": EquipmentType.cable,
        "description": "A rotational cable movement training the obliques through a diagonal chopping pattern.",
        "instructions": (
            "1. Set a cable pulley to the highest position with a rope or handle.\n"
            "2. Stand sideways to the machine, gripping the handle with both hands.\n"
            "3. Pull the handle diagonally across your body from high to low.\n"
            "4. Rotate through your torso, pivoting on the back foot.\n"
            "5. Return slowly to the start and complete all reps before switching sides."
        ),
    },
    {
        "name": "Ab Rollout",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": ["shoulders"],
        "equipment": EquipmentType.other,
        "description": "An ab wheel rollout that challenges the entire anterior core through a long range of motion.",
        "instructions": (
            "1. Kneel on the floor holding an ab wheel with both hands.\n"
            "2. Brace your core and slowly roll the wheel forward.\n"
            "3. Extend as far as you can while keeping your lower back from sagging.\n"
            "4. Pull yourself back to the starting position using your abs.\n"
            "5. Start with partial range and progress to full extension."
        ),
    },
    {
        "name": "Dead Bug",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": [],
        "equipment": EquipmentType.bodyweight,
        "description": "A supine core stability exercise that trains anti-extension.",
        "instructions": (
            "1. Lie on your back with arms extended toward the ceiling and knees at 90 degrees.\n"
            "2. Slowly extend your right arm behind you and your left leg out straight.\n"
            "3. Keep your lower back pressed into the floor.\n"
            "4. Return to the starting position and switch sides.\n"
            "5. Move slowly — the goal is stability, not speed."
        ),
    },
    {
        "name": "Mountain Climber",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": ["shoulders", "quads"],
        "equipment": EquipmentType.bodyweight,
        "description": "A dynamic plank variation that drives the knees toward the chest for core and cardio training.",
        "instructions": (
            "1. Start in a high plank position with hands under shoulders.\n"
            "2. Drive one knee toward your chest.\n"
            "3. Quickly switch legs, bringing the other knee forward.\n"
            "4. Continue alternating at a brisk pace.\n"
            "5. Keep your hips level and avoid bouncing your butt up."
        ),
    },
    {
        "name": "V-Up",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": [],
        "equipment": EquipmentType.bodyweight,
        "description": "A challenging ab exercise where the body folds into a V-shape.",
        "instructions": (
            "1. Lie flat on your back with arms extended overhead and legs straight.\n"
            "2. Simultaneously raise your legs and torso, reaching your hands toward your toes.\n"
            "3. Your body should form a V at the top.\n"
            "4. Lower back down with control.\n"
            "5. Keep your legs and arms as straight as possible throughout."
        ),
    },
    {
        "name": "Decline Sit-Up",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": [],
        "equipment": EquipmentType.bodyweight,
        "description": "A sit-up performed on a decline bench for increased resistance through gravity.",
        "instructions": (
            "1. Hook your feet under the pads of a decline bench.\n"
            "2. Cross your arms over your chest or place hands behind your head.\n"
            "3. Lower your torso back toward the bench.\n"
            "4. Sit up by contracting your abs, bringing your chest toward your thighs.\n"
            "5. Control the lowering phase — do not drop back onto the bench."
        ),
    },
    {
        "name": "Pallof Press",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": [],
        "equipment": EquipmentType.cable,
        "description": "An anti-rotation pressing movement that trains rotational core stability.",
        "instructions": (
            "1. Attach a D-handle to a cable at chest height.\n"
            "2. Stand sideways to the machine, holding the handle at your sternum.\n"
            "3. Press the handle straight out in front of you.\n"
            "4. Hold for 2-3 seconds, resisting the rotation pull.\n"
            "5. Bring the handle back to your chest and repeat."
        ),
    },
    {
        "name": "Dragon Flag",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": [],
        "equipment": EquipmentType.bodyweight,
        "description": "An advanced bodyweight exercise made famous by Bruce Lee, training full-body tension.",
        "instructions": (
            "1. Lie on a bench and grip the edges behind your head.\n"
            "2. Raise your entire body (from shoulders to toes) into a vertical position.\n"
            "3. Slowly lower your body as a rigid plank toward the bench.\n"
            "4. Stop before your lower back touches and reverse the movement.\n"
            "5. Keep your body completely straight — no bending at the hips."
        ),
    },
    {
        "name": "Toe Touch",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": [],
        "equipment": EquipmentType.bodyweight,
        "description": "A lying crunch variation where you reach for your toes to target the upper abs.",
        "instructions": (
            "1. Lie on your back with legs raised straight toward the ceiling.\n"
            "2. Reach your hands up toward your toes by crunching your shoulders off the floor.\n"
            "3. Touch or reach past your toes at the top.\n"
            "4. Lower your shoulders back to the floor.\n"
            "5. Keep your legs as vertical as possible throughout."
        ),
    },
    {
        "name": "Flutter Kicks",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": ["quads"],
        "equipment": EquipmentType.bodyweight,
        "description": "A supine kicking exercise targeting the lower abs and hip flexors.",
        "instructions": (
            "1. Lie flat on your back with hands under your glutes for support.\n"
            "2. Raise both legs a few inches off the floor.\n"
            "3. Alternate kicking each leg up and down in a small, rapid motion.\n"
            "4. Keep your lower back pressed into the floor.\n"
            "5. Continue for the desired number of reps or duration."
        ),
    },
    {
        "name": "Hollow Body Hold",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": [],
        "equipment": EquipmentType.bodyweight,
        "description": "A gymnastic isometric hold that builds total anterior core strength.",
        "instructions": (
            "1. Lie on your back with arms extended overhead and legs straight.\n"
            "2. Press your lower back into the floor and lift your shoulders and legs off the ground.\n"
            "3. Your body should form a slight banana shape.\n"
            "4. Hold this position, keeping your lower back flat.\n"
            "5. If too hard, bend your knees or bring your arms to your sides."
        ),
    },
    {
        "name": "Bird Dog",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": ["glutes"],
        "equipment": EquipmentType.bodyweight,
        "description": "A quadruped exercise that trains core stability and coordination.",
        "instructions": (
            "1. Start on all fours with hands under shoulders and knees under hips.\n"
            "2. Simultaneously extend your right arm forward and left leg backward.\n"
            "3. Hold for 2-3 seconds, keeping your hips level.\n"
            "4. Return to the starting position and switch sides.\n"
            "5. Avoid rotating your hips or arching your back."
        ),
    },
    {
        "name": "Reverse Crunch",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": [],
        "equipment": EquipmentType.bodyweight,
        "description": "A crunch where the legs move toward the chest, targeting the lower abs.",
        "instructions": (
            "1. Lie on your back with hands at your sides or under your hips.\n"
            "2. Raise your legs with knees bent at 90 degrees.\n"
            "3. Curl your hips off the floor, bringing your knees toward your chest.\n"
            "4. Lower your hips back slowly.\n"
            "5. Focus on using your abs to curl the pelvis — not momentum."
        ),
    },
    {
        "name": "Lying Leg Raise",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": [],
        "equipment": EquipmentType.bodyweight,
        "description": "A leg raise performed lying on a bench or the floor, targeting the lower abs.",
        "instructions": (
            "1. Lie flat on your back with legs straight and hands under your glutes.\n"
            "2. Keeping your legs straight, raise them until they point toward the ceiling.\n"
            "3. Lower your legs slowly without letting them touch the floor.\n"
            "4. Maintain contact between your lower back and the floor.\n"
            "5. Bend your knees slightly if you cannot keep your back flat."
        ),
    },
    {
        "name": "Copenhagen Plank",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": ["quads"],
        "equipment": EquipmentType.bodyweight,
        "description": "A side plank variation with the top leg elevated on a bench, targeting the adductors and obliques.",
        "instructions": (
            "1. Lie on your side and place your top foot or knee on a bench.\n"
            "2. Support yourself on your bottom forearm.\n"
            "3. Lift your hips and bottom leg off the floor.\n"
            "4. Hold this position for the desired duration.\n"
            "5. Keep your body in a straight line from head to foot."
        ),
    },
    {
        "name": "L-Sit",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": ["shoulders"],
        "equipment": EquipmentType.bodyweight,
        "description": "An isometric hold with legs extended in front of you while supporting your body on your hands.",
        "instructions": (
            "1. Sit on the floor between two parallettes or on dip bars.\n"
            "2. Place your hands beside your hips and press up, lifting your body off the floor.\n"
            "3. Extend your legs straight in front of you, forming an L-shape.\n"
            "4. Hold this position for as long as possible.\n"
            "5. Keep your legs parallel to the ground and shoulders depressed."
        ),
    },
    {
        "name": "Plank Shoulder Tap",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": ["shoulders"],
        "equipment": EquipmentType.bodyweight,
        "description": "A plank variation that challenges anti-rotation stability by tapping alternate shoulders.",
        "instructions": (
            "1. Start in a high plank position with hands under shoulders.\n"
            "2. Lift one hand and tap the opposite shoulder.\n"
            "3. Return the hand to the floor and tap with the other hand.\n"
            "4. Alternate sides while keeping your hips as still as possible.\n"
            "5. Widen your feet for more stability if needed."
        ),
    },
    {
        "name": "Suitcase Carry",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": ["forearms", "shoulders"],
        "equipment": EquipmentType.dumbbell,
        "description": "A unilateral loaded carry that challenges the lateral core and anti-lateral flexion.",
        "instructions": (
            "1. Hold a heavy dumbbell or kettlebell in one hand at your side.\n"
            "2. Stand tall and brace your core to stay perfectly upright.\n"
            "3. Walk forward with controlled steps without leaning to either side.\n"
            "4. Walk for a set distance or time, then switch hands.\n"
            "5. The goal is to resist side-bending under the asymmetric load."
        ),
    },
    {
        "name": "Windshield Wiper",
        "primary_muscle": MuscleGroup.core,
        "secondary_muscles": [],
        "equipment": EquipmentType.bodyweight,
        "description": "An advanced rotational core exercise performed lying or hanging.",
        "instructions": (
            "1. Lie on your back with arms spread wide for support.\n"
            "2. Raise your legs straight up toward the ceiling.\n"
            "3. Slowly lower both legs to one side, keeping them straight.\n"
            "4. Bring them back to centre and lower to the other side.\n"
            "5. Control the motion through your obliques — avoid crashing to the side."
        ),
    },
    # ── QUADS (23) ────────────────────────────────────────────────────────────
    {
        "name": "Barbell Back Squat",
        "primary_muscle": MuscleGroup.quads,
        "secondary_muscles": ["glutes", "hamstrings", "core"],
        "equipment": EquipmentType.barbell,
        "description": "The king of lower-body exercises, a barbell back squat builds total leg strength.",
        "instructions": (
            "1. Position the bar on your upper traps and unrack with feet shoulder-width apart.\n"
            "2. Brace your core and initiate the squat by breaking at the hips and knees.\n"
            "3. Descend until your thighs are at least parallel to the floor.\n"
            "4. Drive through your full foot to stand back up.\n"
            "5. Keep your chest up and knees tracking over your toes."
        ),
    },
    {
        "name": "Front Squat",
        "primary_muscle": MuscleGroup.quads,
        "secondary_muscles": ["glutes", "core"],
        "equipment": EquipmentType.barbell,
        "description": "A barbell squat with the bar in front, emphasising the quads and demanding a more upright torso.",
        "instructions": (
            "1. Rest the bar across the front of your shoulders with a clean grip or crossed arms.\n"
            "2. Keep your elbows high and chest tall.\n"
            "3. Squat down to full depth, keeping an upright torso.\n"
            "4. Drive up through your quads to return to standing.\n"
            "5. If you lean forward, the bar will roll — stay upright."
        ),
    },
    {
        "name": "Goblet Squat",
        "primary_muscle": MuscleGroup.quads,
        "secondary_muscles": ["glutes", "core"],
        "equipment": EquipmentType.dumbbell,
        "description": "A squat holding a dumbbell at chest height, perfect for learning proper squat mechanics.",
        "instructions": (
            "1. Hold a dumbbell vertically at chest height with both hands cupping one end.\n"
            "2. Stand with feet slightly wider than shoulder-width.\n"
            "3. Squat down, pushing your knees out and keeping your torso upright.\n"
            "4. Descend until your elbows touch the inside of your knees.\n"
            "5. Drive back up to standing."
        ),
    },
    {
        "name": "Leg Press",
        "primary_muscle": MuscleGroup.quads,
        "secondary_muscles": ["glutes", "hamstrings"],
        "equipment": EquipmentType.machine,
        "description": "A machine-based pressing movement for heavy quad loading without spinal compression.",
        "instructions": (
            "1. Sit in the leg press machine with your back flat against the pad.\n"
            "2. Place your feet shoulder-width apart on the platform.\n"
            "3. Release the safety catches and lower the sled by bending your knees.\n"
            "4. Descend until your knees reach about 90 degrees.\n"
            "5. Press the sled back up without locking out your knees completely."
        ),
    },
    {
        "name": "Hack Squat",
        "primary_muscle": MuscleGroup.quads,
        "secondary_muscles": ["glutes"],
        "equipment": EquipmentType.machine,
        "description": "A machine squat that emphasises the quads through a fixed path of motion.",
        "instructions": (
            "1. Stand on the hack squat platform with your back against the pad.\n"
            "2. Position your feet shoulder-width apart, slightly forward on the platform.\n"
            "3. Release the safety and squat down until your thighs are parallel.\n"
            "4. Drive up through your quads to the starting position.\n"
            "5. Keep your back flat against the pad throughout."
        ),
    },
    {
        "name": "Leg Extension",
        "primary_muscle": MuscleGroup.quads,
        "secondary_muscles": [],
        "equipment": EquipmentType.machine,
        "description": "An isolation machine exercise for the quadriceps.",
        "instructions": (
            "1. Sit on the leg extension machine with the pad resting on your lower shins.\n"
            "2. Adjust the back pad so your knees align with the machine's pivot point.\n"
            "3. Extend your legs until they are straight.\n"
            "4. Squeeze the quads at the top.\n"
            "5. Lower slowly — do not let the weight stack drop."
        ),
    },
    {
        "name": "Walking Lunge",
        "primary_muscle": MuscleGroup.quads,
        "secondary_muscles": ["glutes", "hamstrings", "core"],
        "equipment": EquipmentType.dumbbell,
        "description": "A dynamic lunge performed continuously, building single-leg strength and coordination.",
        "instructions": (
            "1. Hold a dumbbell in each hand at your sides.\n"
            "2. Step forward into a lunge, lowering until both knees are at about 90 degrees.\n"
            "3. Push off the front foot and step the rear leg forward into the next lunge.\n"
            "4. Continue alternating legs as you walk forward.\n"
            "5. Keep your torso upright and core engaged throughout."
        ),
    },
    {
        "name": "Bulgarian Split Squat",
        "primary_muscle": MuscleGroup.quads,
        "secondary_muscles": ["glutes", "hamstrings", "core"],
        "equipment": EquipmentType.dumbbell,
        "description": "A single-leg squat with the rear foot elevated, challenging balance and building each leg independently.",
        "instructions": (
            "1. Stand a couple of feet in front of a bench, holding dumbbells at your sides.\n"
            "2. Place the top of your rear foot on the bench behind you.\n"
            "3. Lower your body by bending the front knee until your thigh is parallel to the floor.\n"
            "4. Drive through the front foot to return to standing.\n"
            "5. Keep your torso upright and front knee tracking over your toes."
        ),
    },
    {
        "name": "Sissy Squat",
        "primary_muscle": MuscleGroup.quads,
        "secondary_muscles": [],
        "equipment": EquipmentType.bodyweight,
        "description": "A deep knee-over-toes squat variation isolating the quads with minimal hip involvement.",
        "instructions": (
            "1. Stand upright and hold onto a support with one hand for balance.\n"
            "2. Rise onto the balls of your feet.\n"
            "3. Lean your torso back and bend your knees, lowering your body.\n"
            "4. Descend until your knees are deeply bent and thighs are stretched.\n"
            "5. Push through your toes to return to the starting position."
        ),
    },
    {
        "name": "Box Jump",
        "primary_muscle": MuscleGroup.quads,
        "secondary_muscles": ["glutes", "hamstrings", "calves"],
        "equipment": EquipmentType.bodyweight,
        "description": "An explosive plyometric exercise developing power and fast-twitch muscle fibres.",
        "instructions": (
            "1. Stand in front of a sturdy box or platform.\n"
            "2. Swing your arms back and bend your knees to load.\n"
            "3. Explode upward, jumping onto the box.\n"
            "4. Land softly with both feet, standing up fully on top.\n"
            "5. Step back down (do not jump down) and repeat."
        ),
    },
    {
        "name": "Step-Up",
        "primary_muscle": MuscleGroup.quads,
        "secondary_muscles": ["glutes", "hamstrings"],
        "equipment": EquipmentType.dumbbell,
        "description": "A single-leg exercise stepping onto an elevated surface to build unilateral leg strength.",
        "instructions": (
            "1. Stand in front of a bench or box holding dumbbells at your sides.\n"
            "2. Place one foot fully on the box.\n"
            "3. Drive through the top foot to step up, bringing the trailing leg to meet.\n"
            "4. Step back down with the trailing leg first.\n"
            "5. Complete all reps on one leg before switching."
        ),
    },
    {
        "name": "Wall Sit",
        "primary_muscle": MuscleGroup.quads,
        "secondary_muscles": ["glutes"],
        "equipment": EquipmentType.bodyweight,
        "description": "An isometric hold with your back against a wall and thighs parallel to the ground.",
        "instructions": (
            "1. Stand with your back flat against a wall.\n"
            "2. Slide down until your thighs are parallel to the floor, knees at 90 degrees.\n"
            "3. Keep your back pressed into the wall.\n"
            "4. Hold the position for the desired time.\n"
            "5. Push through your heels to stand back up when finished."
        ),
    },
    {
        "name": "Pistol Squat",
        "primary_muscle": MuscleGroup.quads,
        "secondary_muscles": ["glutes", "core"],
        "equipment": EquipmentType.bodyweight,
        "description": "An advanced single-leg squat requiring strength, balance, and mobility.",
        "instructions": (
            "1. Stand on one leg with the other leg extended in front of you.\n"
            "2. Extend your arms forward for balance.\n"
            "3. Slowly lower yourself on one leg as deep as possible.\n"
            "4. Push through your heel to stand back up.\n"
            "5. Keep your extended leg off the ground throughout the movement."
        ),
    },
    {
        "name": "Zercher Squat",
        "primary_muscle": MuscleGroup.quads,
        "secondary_muscles": ["glutes", "core", "biceps"],
        "equipment": EquipmentType.barbell,
        "description": "A squat with the barbell held in the crooks of your elbows, emphasising the quads and core.",
        "instructions": (
            "1. Position the bar in the crooks of your elbows, clasping your hands together.\n"
            "2. Stand with feet shoulder-width apart.\n"
            "3. Squat down, keeping the bar close to your body and torso upright.\n"
            "4. Drive back up to standing.\n"
            "5. Use a pad or towel on the bar for comfort."
        ),
    },
    {
        "name": "Pause Squat",
        "primary_muscle": MuscleGroup.quads,
        "secondary_muscles": ["glutes", "hamstrings", "core"],
        "equipment": EquipmentType.barbell,
        "description": "A back squat with a deliberate pause at the bottom to eliminate the stretch reflex.",
        "instructions": (
            "1. Set up as you would for a barbell back squat.\n"
            "2. Descend to full depth.\n"
            "3. Hold the bottom position for 2-3 seconds.\n"
            "4. Drive up explosively to standing.\n"
            "5. Use lighter weight than your regular squat — the pause makes it much harder."
        ),
    },
    {
        "name": "Smith Machine Squat",
        "primary_muscle": MuscleGroup.quads,
        "secondary_muscles": ["glutes", "hamstrings"],
        "equipment": EquipmentType.machine,
        "description": "A barbell squat on a Smith machine, providing a guided bar path for additional safety.",
        "instructions": (
            "1. Position yourself under the Smith machine bar with it on your upper traps.\n"
            "2. Place your feet slightly in front of the bar.\n"
            "3. Unrack by rotating the bar and squat down to parallel.\n"
            "4. Press back up to standing.\n"
            "5. Re-rack by rotating the bar hooks into the catches."
        ),
    },
    {
        "name": "Reverse Lunge",
        "primary_muscle": MuscleGroup.quads,
        "secondary_muscles": ["glutes", "hamstrings"],
        "equipment": EquipmentType.dumbbell,
        "description": "A lunge stepping backward, which is generally easier on the knees than a forward lunge.",
        "instructions": (
            "1. Stand holding dumbbells at your sides.\n"
            "2. Step one foot back and lower your knee toward the floor.\n"
            "3. Both knees should form roughly 90-degree angles.\n"
            "4. Push off the back foot and return to standing.\n"
            "5. Alternate legs or complete one side at a time."
        ),
    },
    {
        "name": "Jump Squat",
        "primary_muscle": MuscleGroup.quads,
        "secondary_muscles": ["glutes", "calves"],
        "equipment": EquipmentType.bodyweight,
        "description": "An explosive squat variation for developing lower-body power.",
        "instructions": (
            "1. Stand with feet shoulder-width apart.\n"
            "2. Squat down to about parallel.\n"
            "3. Explode upward, jumping as high as possible.\n"
            "4. Land softly, bending your knees to absorb the impact.\n"
            "5. Immediately descend into the next rep."
        ),
    },
    {
        "name": "Barbell Lunge",
        "primary_muscle": MuscleGroup.quads,
        "secondary_muscles": ["glutes", "hamstrings", "core"],
        "equipment": EquipmentType.barbell,
        "description": "A lunge with a barbell on the back, allowing heavier loading than dumbbells.",
        "instructions": (
            "1. Position a barbell on your upper traps as in a back squat.\n"
            "2. Step forward into a lunge until both knees are at 90 degrees.\n"
            "3. Drive through the front heel to return to standing.\n"
            "4. Alternate legs each rep.\n"
            "5. Keep your torso upright and core braced."
        ),
    },
    {
        "name": "Lateral Lunge",
        "primary_muscle": MuscleGroup.quads,
        "secondary_muscles": ["glutes", "hamstrings"],
        "equipment": EquipmentType.dumbbell,
        "description": "A side lunge that trains the quads and adductors in the frontal plane.",
        "instructions": (
            "1. Stand with feet together holding dumbbells or with body weight only.\n"
            "2. Step wide to one side, pushing your hips back and bending that knee.\n"
            "3. Keep the trailing leg straight.\n"
            "4. Push off the lunging foot to return to the starting position.\n"
            "5. Alternate sides or complete one side first."
        ),
    },
    {
        "name": "Cyclist Squat",
        "primary_muscle": MuscleGroup.quads,
        "secondary_muscles": [],
        "equipment": EquipmentType.dumbbell,
        "description": "A narrow-stance squat with elevated heels that isolates the quads.",
        "instructions": (
            "1. Stand with feet close together, heels elevated on a wedge or small plates.\n"
            "2. Hold a dumbbell at your chest or by your sides.\n"
            "3. Squat straight down, letting your knees travel well forward over your toes.\n"
            "4. Keep your torso upright.\n"
            "5. Press up through the balls of your feet."
        ),
    },
    {
        "name": "Overhead Squat",
        "primary_muscle": MuscleGroup.quads,
        "secondary_muscles": ["core", "shoulders", "glutes"],
        "equipment": EquipmentType.barbell,
        "description": "A squat with the barbell held overhead, demanding extreme mobility and core stability.",
        "instructions": (
            "1. Snatch-grip the bar and press or jerk it overhead.\n"
            "2. Lock your arms out and stabilise the bar overhead.\n"
            "3. Squat down as deep as your mobility allows.\n"
            "4. Keep the bar over mid-foot and your torso as upright as possible.\n"
            "5. Stand back up, maintaining bar position. Start with an empty bar."
        ),
    },
    {
        "name": "Belt Squat",
        "primary_muscle": MuscleGroup.quads,
        "secondary_muscles": ["glutes", "hamstrings"],
        "equipment": EquipmentType.machine,
        "description": "A squat where load is applied via a belt at the hips, sparing the spine.",
        "instructions": (
            "1. Attach the belt around your waist and connect it to the machine's loading pin.\n"
            "2. Stand on the platform with feet shoulder-width apart.\n"
            "3. Squat down to full depth.\n"
            "4. Drive back up through your heels.\n"
            "5. With no spinal loading, you can focus purely on the legs."
        ),
    },
    # ── HAMSTRINGS (15) ───────────────────────────────────────────────────────
    {
        "name": "Romanian Deadlift (Barbell)",
        "primary_muscle": MuscleGroup.hamstrings,
        "secondary_muscles": ["glutes", "back", "core"],
        "equipment": EquipmentType.barbell,
        "description": "A hip-hinge movement that loads the hamstrings and glutes through a deep stretch.",
        "instructions": (
            "1. Stand holding a barbell at hip height with an overhand grip.\n"
            "2. Push your hips back and lower the bar along your legs.\n"
            "3. Keep a slight bend in your knees and your back flat.\n"
            "4. Descend until you feel a strong stretch in the hamstrings.\n"
            "5. Drive your hips forward to return to standing."
        ),
    },
    {
        "name": "Romanian Deadlift (Dumbbell)",
        "primary_muscle": MuscleGroup.hamstrings,
        "secondary_muscles": ["glutes", "back", "core"],
        "equipment": EquipmentType.dumbbell,
        "description": "A dumbbell RDL allowing a more natural hand path and unilateral correction.",
        "instructions": (
            "1. Stand holding a dumbbell in each hand in front of your thighs.\n"
            "2. Hinge at the hips, pushing them back while keeping your spine neutral.\n"
            "3. Lower the dumbbells along your legs until you feel a hamstring stretch.\n"
            "4. Squeeze your glutes to return to standing.\n"
            "5. Keep the dumbbells close to your body throughout."
        ),
    },
    {
        "name": "Lying Leg Curl",
        "primary_muscle": MuscleGroup.hamstrings,
        "secondary_muscles": [],
        "equipment": EquipmentType.machine,
        "description": "A machine isolation exercise for the hamstrings in a prone position.",
        "instructions": (
            "1. Lie face-down on the leg curl machine with the pad on your lower calves.\n"
            "2. Grip the handles for stability.\n"
            "3. Curl your heels toward your glutes by bending the knees.\n"
            "4. Squeeze at the top, then lower slowly.\n"
            "5. Avoid lifting your hips off the pad."
        ),
    },
    {
        "name": "Seated Leg Curl",
        "primary_muscle": MuscleGroup.hamstrings,
        "secondary_muscles": [],
        "equipment": EquipmentType.machine,
        "description": "A machine hamstring curl performed in a seated position.",
        "instructions": (
            "1. Sit in the seated leg curl machine and adjust the pad against your lower calves.\n"
            "2. Secure the thigh pad across your lap.\n"
            "3. Curl your heels under the seat by bending the knees.\n"
            "4. Squeeze the hamstrings at full contraction.\n"
            "5. Return slowly to the starting position."
        ),
    },
    {
        "name": "Good Morning",
        "primary_muscle": MuscleGroup.hamstrings,
        "secondary_muscles": ["glutes", "back", "core"],
        "equipment": EquipmentType.barbell,
        "description": "A barbell hip hinge that loads the posterior chain, similar to an RDL but with the bar on your back.",
        "instructions": (
            "1. Place a barbell on your upper traps as in a squat.\n"
            "2. With feet shoulder-width apart, push your hips back.\n"
            "3. Lower your torso toward the floor with a slight knee bend.\n"
            "4. Stop when your torso is roughly parallel to the floor.\n"
            "5. Extend the hips to return to standing. Start light."
        ),
    },
    {
        "name": "Nordic Hamstring Curl",
        "primary_muscle": MuscleGroup.hamstrings,
        "secondary_muscles": [],
        "equipment": EquipmentType.bodyweight,
        "description": "A bodyweight eccentric hamstring exercise highly effective for injury prevention.",
        "instructions": (
            "1. Kneel on a pad and have a partner hold your ankles (or use an anchor).\n"
            "2. Keep your body straight from knees to head.\n"
            "3. Slowly lower yourself toward the floor by extending at the knees.\n"
            "4. Use your hamstrings to resist the descent as long as possible.\n"
            "5. Catch yourself with your hands and push back up to repeat."
        ),
    },
    {
        "name": "Stiff-Leg Deadlift",
        "primary_muscle": MuscleGroup.hamstrings,
        "secondary_muscles": ["glutes", "back"],
        "equipment": EquipmentType.barbell,
        "description": "A deadlift performed with nearly straight legs to maximise hamstring stretch.",
        "instructions": (
            "1. Stand holding a barbell in front of your thighs.\n"
            "2. With only a very slight knee bend, hinge forward at the hips.\n"
            "3. Lower the bar as far as your hamstring flexibility allows.\n"
            "4. Keep the bar close to your body.\n"
            "5. Return to standing by driving your hips forward."
        ),
    },
    {
        "name": "Sumo Deadlift",
        "primary_muscle": MuscleGroup.hamstrings,
        "secondary_muscles": ["glutes", "quads", "back", "forearms"],
        "equipment": EquipmentType.barbell,
        "description": "A wide-stance deadlift variation that shifts more emphasis to the hips and inner thighs.",
        "instructions": (
            "1. Stand with a wide stance, toes pointed out, the bar over mid-foot.\n"
            "2. Hinge and grip the bar with arms inside your knees.\n"
            "3. Drop your hips, lift your chest, and brace your core.\n"
            "4. Drive through the floor, keeping the bar close to your body.\n"
            "5. Lock out at the top with hips fully extended."
        ),
    },
    {
        "name": "Glute-Ham Raise",
        "primary_muscle": MuscleGroup.hamstrings,
        "secondary_muscles": ["glutes", "core"],
        "equipment": EquipmentType.bodyweight,
        "description": "A posterior chain exercise performed on a GHD machine, working both hip extension and knee flexion.",
        "instructions": (
            "1. Set up on a glute-ham developer with your feet secured and knees on the pad.\n"
            "2. Start with your torso parallel to the floor.\n"
            "3. Raise your body by flexing the knees and extending the hips.\n"
            "4. Finish with your torso vertical.\n"
            "5. Lower slowly back to the starting position."
        ),
    },
    {
        "name": "Single-Leg Deadlift",
        "primary_muscle": MuscleGroup.hamstrings,
        "secondary_muscles": ["glutes", "core"],
        "equipment": EquipmentType.dumbbell,
        "description": "A unilateral hip hinge that builds balance and targets each hamstring independently.",
        "instructions": (
            "1. Stand on one foot holding a dumbbell in the opposite hand.\n"
            "2. Hinge at the hips, extending the free leg behind you.\n"
            "3. Lower the dumbbell toward the floor while keeping your back flat.\n"
            "4. Return to standing by driving through the planted hip.\n"
            "5. Keep your hips square — avoid rotating open."
        ),
    },
    {
        "name": "Kettlebell Swing",
        "primary_muscle": MuscleGroup.hamstrings,
        "secondary_muscles": ["glutes", "core", "shoulders"],
        "equipment": EquipmentType.kettlebell,
        "description": "A ballistic hip-hinge movement for explosive power and posterior chain conditioning.",
        "instructions": (
            "1. Stand with feet wider than shoulder-width, kettlebell on the floor in front of you.\n"
            "2. Hinge at the hips, grip the kettlebell, and hike it back between your legs.\n"
            "3. Explosively drive your hips forward to swing the kettlebell to chest height.\n"
            "4. Let the kettlebell fall back between your legs as you hinge again.\n"
            "5. Power comes from the hips, not the arms — keep your arms relaxed."
        ),
    },
    {
        "name": "Swiss Ball Leg Curl",
        "primary_muscle": MuscleGroup.hamstrings,
        "secondary_muscles": ["glutes", "core"],
        "equipment": EquipmentType.bodyweight,
        "description": "A hamstring curl performed on a stability ball, challenging core stability simultaneously.",
        "instructions": (
            "1. Lie on your back with your heels on top of a Swiss ball.\n"
            "2. Lift your hips off the floor into a bridge position.\n"
            "3. Curl the ball toward your glutes by bending your knees.\n"
            "4. Extend your legs back out without letting your hips drop.\n"
            "5. Keep your core tight and hips elevated throughout."
        ),
    },
    {
        "name": "Banded Good Morning",
        "primary_muscle": MuscleGroup.hamstrings,
        "secondary_muscles": ["glutes", "back"],
        "equipment": EquipmentType.band,
        "description": "A good morning performed with a resistance band for accommodating resistance.",
        "instructions": (
            "1. Stand on a resistance band and loop the other end behind your neck.\n"
            "2. Stand tall with feet shoulder-width apart.\n"
            "3. Push your hips back and lower your torso with a slight knee bend.\n"
            "4. Stop when your torso is roughly parallel to the floor.\n"
            "5. Drive your hips forward to return to standing."
        ),
    },
    {
        "name": "Cable Leg Curl",
        "primary_muscle": MuscleGroup.hamstrings,
        "secondary_muscles": [],
        "equipment": EquipmentType.cable,
        "description": "A standing hamstring curl using an ankle cuff on a low cable.",
        "instructions": (
            "1. Attach an ankle cuff to a low cable pulley and strap it to one ankle.\n"
            "2. Face the machine and hold the frame for balance.\n"
            "3. Curl your heel toward your glute by bending the knee.\n"
            "4. Squeeze at the top, then lower slowly.\n"
            "5. Complete all reps on one leg, then switch."
        ),
    },
    {
        "name": "Dumbbell Leg Curl",
        "primary_muscle": MuscleGroup.hamstrings,
        "secondary_muscles": [],
        "equipment": EquipmentType.dumbbell,
        "description": "A leg curl performed lying face-down on a bench with a dumbbell held between the feet.",
        "instructions": (
            "1. Lie face-down on a flat bench with your knees at the edge.\n"
            "2. Have a partner place a dumbbell between your feet, or squeeze it yourself.\n"
            "3. Curl the dumbbell toward your glutes by bending your knees.\n"
            "4. Lower slowly under control.\n"
            "5. Use a lighter dumbbell and focus on squeezing the hamstrings."
        ),
    },
    # ── GLUTES (17) ───────────────────────────────────────────────────────────
    {
        "name": "Barbell Hip Thrust",
        "primary_muscle": MuscleGroup.glutes,
        "secondary_muscles": ["hamstrings", "core"],
        "equipment": EquipmentType.barbell,
        "description": "The premier glute exercise, driving heavy hip extension from a bench-supported position.",
        "instructions": (
            "1. Sit on the floor with your upper back against a bench and a barbell across your hips.\n"
            "2. Plant your feet flat on the floor, hip-width apart.\n"
            "3. Drive through your heels to lift your hips until they are fully extended.\n"
            "4. Squeeze the glutes hard at the top.\n"
            "5. Lower the hips back down with control. Use a pad on the bar for comfort."
        ),
    },
    {
        "name": "Glute Bridge",
        "primary_muscle": MuscleGroup.glutes,
        "secondary_muscles": ["hamstrings", "core"],
        "equipment": EquipmentType.bodyweight,
        "description": "A bodyweight hip extension performed lying on the floor, activating the glutes.",
        "instructions": (
            "1. Lie on your back with knees bent and feet flat on the floor.\n"
            "2. Drive through your heels to lift your hips toward the ceiling.\n"
            "3. Squeeze your glutes at the top.\n"
            "4. Lower your hips back to the floor.\n"
            "5. Keep your core braced and avoid hyperextending your lower back."
        ),
    },
    {
        "name": "Cable Kickback",
        "primary_muscle": MuscleGroup.glutes,
        "secondary_muscles": ["hamstrings"],
        "equipment": EquipmentType.cable,
        "description": "A cable hip extension performed one leg at a time for glute isolation.",
        "instructions": (
            "1. Attach an ankle cuff to a low cable and strap it to one ankle.\n"
            "2. Face the machine and hold the frame for balance.\n"
            "3. Kick your leg straight back, squeezing the glute.\n"
            "4. Return slowly to the starting position.\n"
            "5. Keep your torso stable — do not arch your lower back."
        ),
    },
    {
        "name": "Sumo Squat",
        "primary_muscle": MuscleGroup.glutes,
        "secondary_muscles": ["quads", "hamstrings", "core"],
        "equipment": EquipmentType.dumbbell,
        "description": "A wide-stance squat emphasising the glutes and inner thighs.",
        "instructions": (
            "1. Stand with feet well beyond shoulder-width, toes pointed outward.\n"
            "2. Hold a dumbbell vertically between your legs.\n"
            "3. Squat down by bending the knees and pushing hips back.\n"
            "4. Descend until your thighs are parallel to the floor.\n"
            "5. Drive through your heels to return to standing."
        ),
    },
    {
        "name": "Cable Pull-Through",
        "primary_muscle": MuscleGroup.glutes,
        "secondary_muscles": ["hamstrings", "back"],
        "equipment": EquipmentType.cable,
        "description": "A hip hinge using a low cable to load the glutes and hamstrings through a pulling motion.",
        "instructions": (
            "1. Attach a rope handle to a low cable and straddle it, facing away.\n"
            "2. Hinge at the hips, reaching the rope between your legs.\n"
            "3. Drive your hips forward explosively, pulling the rope through.\n"
            "4. Stand tall and squeeze your glutes at the top.\n"
            "5. Hinge back and repeat — do not squat this movement."
        ),
    },
    {
        "name": "Donkey Kick",
        "primary_muscle": MuscleGroup.glutes,
        "secondary_muscles": ["hamstrings", "core"],
        "equipment": EquipmentType.bodyweight,
        "description": "A kneeling hip extension exercise that targets the gluteus maximus.",
        "instructions": (
            "1. Start on all fours with hands under shoulders and knees under hips.\n"
            "2. Keeping one knee bent at 90 degrees, drive your foot toward the ceiling.\n"
            "3. Squeeze the glute at the top.\n"
            "4. Lower back to the start without touching the floor.\n"
            "5. Complete all reps on one side, then switch."
        ),
    },
    {
        "name": "Fire Hydrant",
        "primary_muscle": MuscleGroup.glutes,
        "secondary_muscles": ["core"],
        "equipment": EquipmentType.bodyweight,
        "description": "A hip abduction from a quadruped position, targeting the gluteus medius.",
        "instructions": (
            "1. Start on all fours with a flat back.\n"
            "2. Keeping your knee bent, lift one leg out to the side.\n"
            "3. Raise it as high as comfortably possible.\n"
            "4. Lower slowly back to the starting position.\n"
            "5. Keep your hips level and avoid shifting your weight."
        ),
    },
    {
        "name": "Banded Clamshell",
        "primary_muscle": MuscleGroup.glutes,
        "secondary_muscles": [],
        "equipment": EquipmentType.band,
        "description": "A side-lying hip rotation with a band, activating the gluteus medius and external rotators.",
        "instructions": (
            "1. Lie on your side with a resistance band around both knees.\n"
            "2. Bend your knees to about 90 degrees with feet together.\n"
            "3. Open your top knee toward the ceiling like a clamshell.\n"
            "4. Squeeze at the top, then lower slowly.\n"
            "5. Keep your feet together and hips stacked throughout."
        ),
    },
    {
        "name": "Step-Up (High)",
        "primary_muscle": MuscleGroup.glutes,
        "secondary_muscles": ["quads", "hamstrings"],
        "equipment": EquipmentType.dumbbell,
        "description": "A step-up onto a higher platform that increases glute recruitment.",
        "instructions": (
            "1. Stand in front of a high box or bench (at or above knee height).\n"
            "2. Hold dumbbells at your sides.\n"
            "3. Place one foot on the box and drive through the heel to step up.\n"
            "4. Stand fully on the box, then step back down under control.\n"
            "5. The higher the box, the more glute activation. Use a secure surface."
        ),
    },
    {
        "name": "Single-Leg Hip Thrust",
        "primary_muscle": MuscleGroup.glutes,
        "secondary_muscles": ["hamstrings", "core"],
        "equipment": EquipmentType.bodyweight,
        "description": "A hip thrust performed on one leg to address glute imbalances.",
        "instructions": (
            "1. Set up for a hip thrust with your upper back on a bench.\n"
            "2. Extend one leg straight out or hold it in the air.\n"
            "3. Drive through the planted foot to thrust your hips up.\n"
            "4. Squeeze the glute at the top.\n"
            "5. Lower under control and complete all reps before switching legs."
        ),
    },
    {
        "name": "Frog Pump",
        "primary_muscle": MuscleGroup.glutes,
        "secondary_muscles": ["hamstrings"],
        "equipment": EquipmentType.bodyweight,
        "description": "A glute bridge variation with the soles of the feet together, isolating the glutes.",
        "instructions": (
            "1. Lie on your back and place the soles of your feet together, knees falling outward.\n"
            "2. Thrust your hips upward by squeezing the glutes.\n"
            "3. Squeeze hard at the top.\n"
            "4. Lower back to the floor.\n"
            "5. The feet position reduces hamstring involvement, isolating the glutes."
        ),
    },
    {
        "name": "Hip Abduction (Machine)",
        "primary_muscle": MuscleGroup.glutes,
        "secondary_muscles": [],
        "equipment": EquipmentType.machine,
        "description": "A machine exercise that targets the hip abductors and gluteus medius.",
        "instructions": (
            "1. Sit in the hip abduction machine with your legs inside the pads.\n"
            "2. Push your legs outward against the resistance.\n"
            "3. Squeeze the outer glutes at full range of motion.\n"
            "4. Return slowly to the starting position.\n"
            "5. Lean slightly forward to increase gluteus maximus engagement."
        ),
    },
    {
        "name": "Lateral Band Walk",
        "primary_muscle": MuscleGroup.glutes,
        "secondary_muscles": [],
        "equipment": EquipmentType.band,
        "description": "A banded side-stepping exercise for activating the gluteus medius.",
        "instructions": (
            "1. Place a resistance band around your legs just above the knees (or around ankles).\n"
            "2. Stand in a half-squat position.\n"
            "3. Step sideways, maintaining tension on the band.\n"
            "4. Keep your toes pointed forward and hips level.\n"
            "5. Walk the desired distance, then reverse direction."
        ),
    },
    {
        "name": "Curtsy Lunge",
        "primary_muscle": MuscleGroup.glutes,
        "secondary_muscles": ["quads", "hamstrings"],
        "equipment": EquipmentType.dumbbell,
        "description": "A lunge stepping diagonally behind you to target the glute medius and outer hip.",
        "instructions": (
            "1. Stand holding dumbbells at your sides.\n"
            "2. Step one foot diagonally behind the other, as if performing a curtsy.\n"
            "3. Lower until your front thigh is parallel to the floor.\n"
            "4. Push through the front foot to return to standing.\n"
            "5. Alternate legs or complete one side at a time."
        ),
    },
    {
        "name": "Glute Kickback (Machine)",
        "primary_muscle": MuscleGroup.glutes,
        "secondary_muscles": ["hamstrings"],
        "equipment": EquipmentType.machine,
        "description": "A machine-based kickback that isolates the gluteus maximus.",
        "instructions": (
            "1. Stand on the machine platform and position one foot on the kickback pad.\n"
            "2. Drive the pad backward by extending your hip.\n"
            "3. Squeeze the glute at full extension.\n"
            "4. Return slowly to the starting position.\n"
            "5. Complete all reps on one leg, then switch."
        ),
    },
    {
        "name": "Smith Machine Hip Thrust",
        "primary_muscle": MuscleGroup.glutes,
        "secondary_muscles": ["hamstrings", "core"],
        "equipment": EquipmentType.machine,
        "description": "A hip thrust performed on a Smith machine for a guided bar path and easy setup.",
        "instructions": (
            "1. Set a bench perpendicular to a Smith machine and sit with your upper back against it.\n"
            "2. Position the bar across your hips with a pad.\n"
            "3. Plant your feet and drive your hips up, unracking the bar.\n"
            "4. Squeeze the glutes at the top, then lower under control.\n"
            "5. Rotate the bar to re-rack when finished."
        ),
    },
    {
        "name": "Cable Hip Abduction",
        "primary_muscle": MuscleGroup.glutes,
        "secondary_muscles": [],
        "equipment": EquipmentType.cable,
        "description": "A standing cable abduction to target the gluteus medius and hip abductors.",
        "instructions": (
            "1. Attach an ankle cuff to a low cable and strap it to your outer ankle.\n"
            "2. Stand sideways to the machine, holding the frame for support.\n"
            "3. Lift the cuffed leg out to the side against the cable resistance.\n"
            "4. Pause at the top, then lower slowly.\n"
            "5. Complete all reps, then switch legs."
        ),
    },
    # ── CALVES (8) ────────────────────────────────────────────────────────────
    {
        "name": "Standing Calf Raise",
        "primary_muscle": MuscleGroup.calves,
        "secondary_muscles": [],
        "equipment": EquipmentType.machine,
        "description": "A machine calf raise performed standing, targeting the gastrocnemius.",
        "instructions": (
            "1. Stand on the platform of a standing calf raise machine with the pads on your shoulders.\n"
            "2. Lower your heels below the platform for a full stretch.\n"
            "3. Rise up onto your toes as high as possible.\n"
            "4. Squeeze the calves at the top.\n"
            "5. Lower slowly and repeat. Use a full range of motion."
        ),
    },
    {
        "name": "Seated Calf Raise (Machine)",
        "primary_muscle": MuscleGroup.calves,
        "secondary_muscles": [],
        "equipment": EquipmentType.machine,
        "description": "A seated calf raise emphasising the soleus muscle under the gastrocnemius.",
        "instructions": (
            "1. Sit in the seated calf raise machine with the pad across your lower thighs.\n"
            "2. Place the balls of your feet on the platform with heels hanging off.\n"
            "3. Release the safety and lower your heels for a full stretch.\n"
            "4. Push up onto your toes and squeeze.\n"
            "5. The seated position isolates the soleus — use a slow tempo."
        ),
    },
    {
        "name": "Single-Leg Calf Raise",
        "primary_muscle": MuscleGroup.calves,
        "secondary_muscles": [],
        "equipment": EquipmentType.bodyweight,
        "description": "A calf raise on one leg to increase intensity and address imbalances.",
        "instructions": (
            "1. Stand on the edge of a step on one foot, holding a wall or rail for balance.\n"
            "2. Lower your heel below the step for a full stretch.\n"
            "3. Rise up onto your toes as high as possible.\n"
            "4. Squeeze at the top, then lower slowly.\n"
            "5. Complete all reps, then switch legs."
        ),
    },
    {
        "name": "Donkey Calf Raise",
        "primary_muscle": MuscleGroup.calves,
        "secondary_muscles": [],
        "equipment": EquipmentType.machine,
        "description": "A calf raise performed in a bent-over position, allowing a deep stretch of the gastrocnemius.",
        "instructions": (
            "1. Position yourself on a donkey calf raise machine or bend at the hips with a partner on your back.\n"
            "2. Place the balls of your feet on the edge of the platform.\n"
            "3. Lower your heels for a deep stretch.\n"
            "4. Rise up on your toes as high as you can.\n"
            "5. The bent-over position pre-stretches the calves for a greater range of motion."
        ),
    },
    {
        "name": "Calf Press on Leg Press",
        "primary_muscle": MuscleGroup.calves,
        "secondary_muscles": [],
        "equipment": EquipmentType.machine,
        "description": "A calf raise performed on a leg press machine for heavy calf loading.",
        "instructions": (
            "1. Sit in a leg press machine and place only the balls of your feet at the bottom edge of the platform.\n"
            "2. Extend your legs to unrack the sled, keeping them nearly straight.\n"
            "3. Press the platform away by pointing your toes (plantar flexion).\n"
            "4. Lower slowly, letting your toes come back toward you.\n"
            "5. Do not bend your knees — this is purely a calf movement."
        ),
    },
    {
        "name": "Jump Rope",
        "primary_muscle": MuscleGroup.calves,
        "secondary_muscles": ["core", "shoulders"],
        "equipment": EquipmentType.other,
        "description": "A classic conditioning exercise that trains the calves through repeated jumping.",
        "instructions": (
            "1. Hold a jump rope with handles in each hand.\n"
            "2. Swing the rope over your head and jump as it passes under your feet.\n"
            "3. Stay on the balls of your feet, using your calves to spring up.\n"
            "4. Keep your jumps low and your wrists doing most of the rotation.\n"
            "5. Maintain a steady rhythm for the desired duration or reps."
        ),
    },
    {
        "name": "Smith Machine Calf Raise",
        "primary_muscle": MuscleGroup.calves,
        "secondary_muscles": [],
        "equipment": EquipmentType.machine,
        "description": "A standing calf raise using the Smith machine for guided support and easy loading.",
        "instructions": (
            "1. Set the Smith machine bar on your traps and stand on a raised platform or plates.\n"
            "2. Unrack the bar by rotating the hooks.\n"
            "3. Lower your heels below the platform for a stretch.\n"
            "4. Rise up onto your toes and squeeze at the top.\n"
            "5. Lower with control and repeat."
        ),
    },
    {
        "name": "Seated Calf Raise (Barbell)",
        "primary_muscle": MuscleGroup.calves,
        "secondary_muscles": [],
        "equipment": EquipmentType.barbell,
        "description": "A seated calf raise using a barbell across the knees for gyms without a dedicated machine.",
        "instructions": (
            "1. Sit on a bench with the balls of your feet on a raised surface.\n"
            "2. Place a padded barbell across your lower thighs.\n"
            "3. Lower your heels below the raised surface for a stretch.\n"
            "4. Push up onto your toes, squeezing the calves.\n"
            "5. Lower slowly. Use a towel or pad to cushion the bar."
        ),
    },
]


async def seed() -> None:
    """Insert seed exercises if the database is empty."""
    async with AsyncSessionLocal() as session:
        count = await session.scalar(select(func.count()).select_from(Exercise))
        if count and count > 0:
            print(f"Database already has {count} exercises — skipping seed.")
            return

        exercises = [Exercise(**data) for data in EXERCISES]
        session.add_all(exercises)
        await session.commit()
        print(f"Seeded {len(exercises)} exercises across all muscle groups.")

        # Print a quick breakdown by muscle group
        breakdown: dict[str, int] = {}
        for ex in EXERCISES:
            group = ex["primary_muscle"].value
            breakdown[group] = breakdown.get(group, 0) + 1
        for group, n in sorted(breakdown.items(), key=lambda x: -x[1]):
            print(f"  {group:<12s} {n}")


if __name__ == "__main__":
    asyncio.run(seed())
