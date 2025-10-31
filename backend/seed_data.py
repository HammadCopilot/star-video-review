"""
Seed database with initial data:
- Admin user
- Best practices criteria
- Sample videos from provided URLs
"""

from app import create_app
from models import db, User, BestPractice, Video
from datetime import datetime

def seed_database():
    """Seed initial data"""
    app = create_app()
    
    with app.app_context():
        print("Starting database seeding...")
        
        # Create admin user
        admin = User.query.filter_by(email='admin@star.com').first()
        if not admin:
            admin = User(
                email='admin@star.com',
                first_name='Admin',
                last_name='User',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            print("✓ Admin user created (admin@star.com / admin123)")
        
        # Create reviewer user
        reviewer = User.query.filter_by(email='reviewer@star.com').first()
        if not reviewer:
            reviewer = User(
                email='reviewer@star.com',
                first_name='Reviewer',
                last_name='User',
                role='reviewer',
                is_active=True
            )
            reviewer.set_password('reviewer123')
            db.session.add(reviewer)
            print("✓ Reviewer user created (reviewer@star.com / reviewer123)")
        
        db.session.commit()
        
        # Seed best practices
        if BestPractice.query.count() == 0:
            best_practices = [
                # Discrete Trial (13 practices)
                {
                    'category': 'discrete_trial',
                    'title': 'Consistent Cue Usage',
                    'description': 'Uses consistent cue based on lesson (e.g., "give me" or "match")',
                    'criteria': 'The teacher should use the same cue throughout all trials',
                    'is_positive': True,
                    'order': 1
                },
                {
                    'category': 'discrete_trial',
                    'title': 'Immediate Re-stating Before Praise',
                    'description': 'Immediately after child follows cue correctly, re-states the name of the item prior to verbal praise',
                    'criteria': 'Teacher says item name immediately before giving praise',
                    'is_positive': True,
                    'order': 2
                },
                {
                    'category': 'discrete_trial',
                    'title': 'Error Correction Procedure',
                    'description': 'Follows proper error correction: start trial over, repeat cue, help child get it right, verbal praise only, then try again',
                    'criteria': 'When child makes error, teacher implements full error correction sequence',
                    'is_positive': True,
                    'order': 3
                },
                {
                    'category': 'discrete_trial',
                    'title': 'Reinforces Hands Down and Sitting',
                    'description': 'Reinforces hands down and sitting throughout the session',
                    'criteria': 'Teacher actively reinforces proper sitting posture and hands down',
                    'is_positive': True,
                    'order': 4
                },
                {
                    'category': 'discrete_trial',
                    'title': 'Clear Expressive Cue',
                    'description': 'For expressive lessons, immediately asks "what is it?" or "what are they doing?"',
                    'criteria': 'Expressive lessons use appropriate question format',
                    'is_positive': True,
                    'order': 5
                },
                {
                    'category': 'discrete_trial',
                    'title': 'Reinforcer Only for Independent Response',
                    'description': 'Provides reinforcer only when child completes task independently',
                    'criteria': 'Access to preferred items only given for independent correct responses',
                    'is_positive': True,
                    'order': 6
                },
                {
                    'category': 'discrete_trial',
                    'title': 'Inconsistent Cue',
                    'description': 'Uses different cues or inconsistent language across trials',
                    'criteria': 'Teacher varies the cue or uses different wording',
                    'is_positive': False,
                    'order': 7
                },
                {
                    'category': 'discrete_trial',
                    'title': 'Missing Re-statement',
                    'description': 'Fails to re-state item name before giving praise',
                    'criteria': 'Goes directly to praise without labeling the item',
                    'is_positive': False,
                    'order': 8
                },
                {
                    'category': 'discrete_trial',
                    'title': 'Incorrect Error Correction',
                    'description': 'Does not follow proper error correction procedure',
                    'criteria': 'Skips steps or provides reinforcer after prompted response',
                    'is_positive': False,
                    'order': 9
                },
                {
                    'category': 'discrete_trial',
                    'title': 'Excessive Language',
                    'description': 'Uses too much language or adds unnecessary words to the cue',
                    'criteria': 'Cue includes extra words beyond the key direction',
                    'is_positive': False,
                    'order': 10
                },
                {
                    'category': 'discrete_trial',
                    'title': 'Poor Positioning',
                    'description': 'Teacher positioned incorrectly (should be at eye level, facing child)',
                    'criteria': 'Physical positioning not optimal for instruction',
                    'is_positive': False,
                    'order': 11
                },
                {
                    'category': 'discrete_trial',
                    'title': 'Delayed Reinforcement',
                    'description': 'Waits too long to provide reinforcement after correct response',
                    'criteria': 'Reinforcement not immediate (should be within 1-2 seconds)',
                    'is_positive': False,
                    'order': 12
                },
                {
                    'category': 'discrete_trial',
                    'title': 'Materials Not Ready',
                    'description': 'Materials not organized or prepared before session',
                    'criteria': 'Teacher fumbles with materials or has to search for items',
                    'is_positive': False,
                    'order': 13
                },
                
                # Pivotal Response Training (12 practices)
                {
                    'category': 'pivotal_response',
                    'title': 'Following Student Lead',
                    'description': 'Follows the student\'s lead and what they want to play with',
                    'criteria': 'Teacher observes child\'s interests and builds on them',
                    'is_positive': True,
                    'order': 1
                },
                {
                    'category': 'pivotal_response',
                    'title': 'Language Trial Execution',
                    'description': 'Withholds preferred item and prompts child to babble, make sound, or repeat item name',
                    'criteria': 'Implements language trial with prompt and immediate access to item',
                    'is_positive': True,
                    'order': 2
                },
                {
                    'category': 'pivotal_response',
                    'title': 'Play Trial with Modeling',
                    'description': 'Models appropriate play, says "do this", and gives child chance to imitate',
                    'criteria': 'Clear play modeling followed by imitation opportunity',
                    'is_positive': True,
                    'order': 3
                },
                {
                    'category': 'pivotal_response',
                    'title': 'Engaging Toy Selection',
                    'description': 'Uses toys with parts/pieces that are engaging, motivating, and have multiple purposes',
                    'criteria': 'Toy selection appropriate for PRT (not single-function toys)',
                    'is_positive': True,
                    'order': 4
                },
                {
                    'category': 'pivotal_response',
                    'title': 'Natural Reinforcement',
                    'description': 'Reinforcement is natural and directly related to the response',
                    'criteria': 'Child gets the item they requested or activity they attempted',
                    'is_positive': True,
                    'order': 5
                },
                {
                    'category': 'pivotal_response',
                    'title': 'Multiple Cues',
                    'description': 'Presents multiple cues or choices to maintain variety',
                    'criteria': 'Varies activities and materials throughout session',
                    'is_positive': True,
                    'order': 6
                },
                {
                    'category': 'pivotal_response',
                    'title': 'Turn Taking',
                    'description': 'Incorporates turn-taking in play activities',
                    'criteria': 'Teacher and child take turns with materials/activities',
                    'is_positive': True,
                    'order': 7
                },
                {
                    'category': 'pivotal_response',
                    'title': 'Not Following Child Lead',
                    'description': 'Teacher directs play without considering child\'s interests',
                    'criteria': 'Imposes activities child is not interested in',
                    'is_positive': False,
                    'order': 8
                },
                {
                    'category': 'pivotal_response',
                    'title': 'Missing Language Opportunities',
                    'description': 'Fails to create language trials or prompts',
                    'criteria': 'Gives items without requiring any communication attempt',
                    'is_positive': False,
                    'order': 9
                },
                {
                    'category': 'pivotal_response',
                    'title': 'Poor Toy Selection',
                    'description': 'Uses single-function or non-engaging toys',
                    'criteria': 'Toys don\'t support PRT principles or child engagement',
                    'is_positive': False,
                    'order': 10
                },
                {
                    'category': 'pivotal_response',
                    'title': 'Unclear Modeling',
                    'description': 'Play modeling is unclear or not demonstrative',
                    'criteria': 'Child cannot clearly see what they should imitate',
                    'is_positive': False,
                    'order': 11
                },
                {
                    'category': 'pivotal_response',
                    'title': 'Low Energy/Affect',
                    'description': 'Teacher shows low enthusiasm or flat affect',
                    'criteria': 'Energy level does not match child\'s excitement or engagement needs',
                    'is_positive': False,
                    'order': 12
                },
                
                # Functional Routines (15 practices)
                {
                    'category': 'functional_routines',
                    'title': 'Visual Supports with Minimal Language',
                    'description': 'Uses visual supports and minimal language',
                    'criteria': 'Visual cues present and language kept to key words only',
                    'is_positive': True,
                    'order': 1
                },
                {
                    'category': 'functional_routines',
                    'title': 'Prompting from Behind',
                    'description': 'Prompts from behind the student',
                    'criteria': 'Teacher physically positioned behind child when prompting',
                    'is_positive': True,
                    'order': 2
                },
                {
                    'category': 'functional_routines',
                    'title': 'Reverse Chaining',
                    'description': 'Uses reverse chaining - does entire routine and child does last step first',
                    'criteria': 'Child completes final step independently before earlier steps',
                    'is_positive': True,
                    'order': 3
                },
                {
                    'category': 'functional_routines',
                    'title': 'Reinforcement During Routine',
                    'description': 'Uses reinforcement during the routine',
                    'criteria': 'Provides praise or reinforcement throughout the activity',
                    'is_positive': True,
                    'order': 4
                },
                {
                    'category': 'functional_routines',
                    'title': 'Visual Schedules for Transitions',
                    'description': 'Uses visual schedules to help with transitions',
                    'criteria': 'Visual schedule visible and referenced during transitions',
                    'is_positive': True,
                    'order': 5
                },
                {
                    'category': 'functional_routines',
                    'title': 'Consistent Routine Structure',
                    'description': 'Maintains consistent structure and sequence',
                    'criteria': 'Steps completed in same order each time',
                    'is_positive': True,
                    'order': 6
                },
                {
                    'category': 'functional_routines',
                    'title': 'Appropriate Wait Time',
                    'description': 'Provides adequate wait time for child to respond',
                    'criteria': 'Waits 3-5 seconds before prompting',
                    'is_positive': True,
                    'order': 7
                },
                {
                    'category': 'functional_routines',
                    'title': 'Fading Prompts Appropriately',
                    'description': 'Systematically fades prompts as child gains independence',
                    'criteria': 'Uses least-to-most or most-to-least prompting hierarchy',
                    'is_positive': True,
                    'order': 8
                },
                {
                    'category': 'functional_routines',
                    'title': 'Excessive Language',
                    'description': 'Uses too much language during the routine',
                    'criteria': 'Uses full sentences or explanations instead of key words',
                    'is_positive': False,
                    'order': 9
                },
                {
                    'category': 'functional_routines',
                    'title': 'Prompting from Front',
                    'description': 'Prompts from in front of student rather than behind',
                    'criteria': 'Teacher positioned incorrectly for prompting',
                    'is_positive': False,
                    'order': 10
                },
                {
                    'category': 'functional_routines',
                    'title': 'Not Using Reverse Chaining',
                    'description': 'Attempts to teach all steps at once or starts from beginning',
                    'criteria': 'Chaining procedure not implemented correctly',
                    'is_positive': False,
                    'order': 11
                },
                {
                    'category': 'functional_routines',
                    'title': 'Missing Visual Supports',
                    'description': 'Does not use visual supports or schedules',
                    'criteria': 'Relies solely on verbal instructions',
                    'is_positive': False,
                    'order': 12
                },
                {
                    'category': 'functional_routines',
                    'title': 'Inconsistent Routine',
                    'description': 'Routine steps vary or are completed out of order',
                    'criteria': 'Lacks consistency across sessions',
                    'is_positive': False,
                    'order': 13
                },
                {
                    'category': 'functional_routines',
                    'title': 'No Wait Time',
                    'description': 'Prompts immediately without giving child time to respond',
                    'criteria': 'Does not allow adequate wait time (minimum 3 seconds)',
                    'is_positive': False,
                    'order': 14
                },
                {
                    'category': 'functional_routines',
                    'title': 'Over-Prompting',
                    'description': 'Provides more prompting than necessary, hindering independence',
                    'criteria': 'Uses hand-over-hand when child could do with less intrusive prompt',
                    'is_positive': False,
                    'order': 15
                }
            ]
            
            for practice_data in best_practices:
                practice = BestPractice(**practice_data)
                db.session.add(practice)
            
            print(f"✓ Seeded {len(best_practices)} best practices")
            db.session.commit()
        
        # Seed sample videos
        if Video.query.count() == 0:
            sample_videos = [
                {
                    'title': 'PRT Example 1 - Following Student Lead',
                    'url': 'https://cdn.jwplayer.com/videos/Mi1eph4z-pX8xjuXl.mp4',
                    'category': 'pivotal_response',
                    'description': 'Example of Pivotal Response Training with live coaching'
                },
                {
                    'title': 'PRT Example 2 - Language Trial',
                    'url': 'https://cdn.jwplayer.com/videos/f9hHLzoi-EV8vzaWw.mp4',
                    'category': 'pivotal_response',
                    'description': 'Example of Pivotal Response Training with live coaching'
                },
                {
                    'title': 'PRT Example 3 - Play Modeling',
                    'url': 'https://cdn.jwplayer.com/videos/OZkNcMHf-pX8xjuXl.mp4',
                    'category': 'pivotal_response',
                    'description': 'Example of Pivotal Response Training with live coaching'
                },
                {
                    'title': 'PRT Example 4 - Turn Taking',
                    'url': 'https://cdn.jwplayer.com/videos/Rl8CNK3t-Lf6dS7We.mp4',
                    'category': 'pivotal_response',
                    'description': 'Example of Pivotal Response Training with live coaching'
                },
                {
                    'title': 'Discrete Trial - Error Correction',
                    'url': 'https://cdn.jwplayer.com/videos/xeEBsa4h-Lf6dS7We.mp4',
                    'category': 'discrete_trial',
                    'description': 'Example of Discrete Trial training with proper error correction'
                },
                {
                    'title': 'Functional Routines - Small Group Activity',
                    'url': 'https://cdn.jwplayer.com/videos/2YJx5qY3-EV8vzaWw.mp4',
                    'category': 'functional_routines',
                    'description': 'Small group activity - generalizing skills from Discrete Trial'
                },
                {
                    'title': 'Discrete Trial - Expressive Lesson',
                    'url': 'https://cdn.jwplayer.com/videos/4kLmZsjC-pX8xjuXl.mp4',
                    'category': 'discrete_trial',
                    'description': 'Excellent example with no errors - consistent cue usage and proper procedure'
                },
                {
                    'title': 'Discrete Trial - Give Me Verb',
                    'url': 'https://cdn.jwplayer.com/videos/fFLdIJiL-pX8xjuXl.mp4',
                    'category': 'discrete_trial',
                    'description': 'Discrete trial teaching session'
                },
                {
                    'title': 'Discrete Trial - Receptive Lesson',
                    'url': 'https://cdn.jwplayer.com/videos/UJeIddSP-EV8vzaWw.mp4',
                    'category': 'discrete_trial',
                    'description': 'Discrete trial teaching session'
                },
                {
                    'title': 'Discrete Trial - Matching Task',
                    'url': 'https://cdn.jwplayer.com/videos/S2KysTEs-pX8xjuXl.mp4',
                    'category': 'discrete_trial',
                    'description': 'Discrete trial matching activity'
                }
            ]
            
            for video_data in sample_videos:
                video = Video(
                    title=video_data['title'],
                    description=video_data['description'],
                    source_type='url',
                    url=video_data['url'],
                    uploader_id=admin.id,
                    category=video_data['category']
                )
                db.session.add(video)
            
            print(f"✓ Seeded {len(sample_videos)} sample videos")
            db.session.commit()
        
        print("\n✅ Database seeding completed successfully!")
        print("\nTest Accounts:")
        print("  Admin: admin@star.com / admin123")
        print("  Reviewer: reviewer@star.com / reviewer123")


if __name__ == '__main__':
    seed_database()

