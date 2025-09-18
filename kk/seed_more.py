import argparse
import random
from datetime import datetime, timedelta

from app import app, db, Car
from app import populate_car_models, seed_example_listings


def top_up_minimum(target_total: int) -> None:
    with app.app_context():
        # Ensure model catalog exists
        populate_car_models()
        # Top up using existing seeder (idempotent up to target)
        seed_example_listings(target_total)


def clone_near_existing(base_count: int = 40) -> None:
    """Clone around an existing car's brand+model so similar/related will have content.
    Picks the most recently created car and generates variants with small differences.
    """
    with app.app_context():
        base_car: Car | None = db.session.query(Car).order_by(Car.created_at.desc()).first()
        if not base_car:
            return
        for i in range(base_count):
            price = base_car.price if base_car.price is not None else random.randint(5000, 60000)
            price_variant = max(1000, int(price + random.randint(-8000, 8000)))
            year_variant = base_car.year if base_car.year else random.randint(2005, datetime.utcnow().year)
            mileage_variant = random.randint(0, 220_000)
            created_offset_days = random.randint(0, 180)
            clone = Car(
                title=f"{(base_car.brand or '').title()} {(base_car.model or '').title()} Base {i+1}",
                brand=base_car.brand,
                model=base_car.model,
                trim=base_car.trim or 'Base',
                year=year_variant,
                mileage=mileage_variant,
                price=price_variant,
                title_status=base_car.title_status or 'clean',
                damaged_parts=None,
                transmission=base_car.transmission or 'automatic',
                fuel_type=base_car.fuel_type or 'gasoline',
                color=base_car.color or 'black',
                cylinder_count=base_car.cylinder_count or 4,
                engine_size=base_car.engine_size or 2.0,
                import_country='us',
                body_type=base_car.body_type or 'sedan',
                seating=base_car.seating or 5,
                drive_type=base_car.drive_type or 'fwd',
                license_plate_type=base_car.license_plate_type or 'private',
                city=base_car.city or 'baghdad',
                condition=base_car.condition or 'used',
                user_id=base_car.user_id,
                status='active',
                created_at=datetime.utcnow() - timedelta(days=created_offset_days),
            )
            db.session.add(clone)
        db.session.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed more listings for development")
    parser.add_argument("--min", type=int, default=300, help="Minimum total listings to ensure")
    parser.add_argument("--clone", type=int, default=40, help="How many clones to add around latest car")
    args = parser.parse_args()

    top_up_minimum(args.min)
    clone_near_existing(args.clone)
    with app.app_context():
        total = db.session.query(Car).count()
        print(f"Seeding complete. Total cars: {total}")


if __name__ == "__main__":
    main()


