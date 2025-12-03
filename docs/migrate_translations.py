#!/usr/bin/env python3
"""Script to migrate French translations from old docs/fr/ to PO files.

This script:
1. Reads English source files (docs/source/*.md)
2. Reads old French translations (docs/fr/*.md)
3. Matches English text to French translations
4. Populates PO files with translations

Usage:
    python migrate_translations.py
"""

import re
import polib
from pathlib import Path
from difflib import SequenceMatcher


def normalize_text(text):
    """Normalize text for comparison."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove markdown formatting for matching
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic
    text = re.sub(r'`([^`]+)`', r'\1', text)        # Code
    return text


def extract_paragraphs(md_file):
    """Extract paragraphs and their normalized versions from markdown file."""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by empty lines to get paragraphs
    paragraphs = []
    current_para = []

    for line in content.split('\n'):
        line = line.strip()

        if line:
            current_para.append(line)
        else:
            if current_para:
                para_text = ' '.join(current_para)
                if para_text:  # Skip empty paragraphs
                    paragraphs.append(para_text)
                current_para = []

    # Don't forget last paragraph
    if current_para:
        para_text = ' '.join(current_para)
        if para_text:
            paragraphs.append(para_text)

    return paragraphs


def find_best_match(en_text, fr_paragraphs, threshold=0.3):
    """Find best matching French paragraph for English text."""
    en_normalized = normalize_text(en_text)
    best_match = None
    best_ratio = 0

    for fr_text in fr_paragraphs:
        fr_normalized = normalize_text(fr_text)

        # Try matching structure (similar length, similar word count)
        en_words = len(en_normalized.split())
        fr_words = len(fr_normalized.split())

        if abs(en_words - fr_words) > max(en_words, fr_words) * 0.5:
            continue  # Skip if word counts are too different

        # Use sequence matcher for fuzzy matching
        ratio = SequenceMatcher(None, en_normalized.lower(), fr_normalized.lower()).ratio()

        if ratio > best_ratio and ratio > threshold:
            best_ratio = ratio
            best_match = fr_text

    return best_match if best_ratio > threshold else None


def migrate_file(po_file, en_file, fr_file):
    """Migrate translations for a single file."""
    print(f"\n{'='*70}")
    print(f"Processing: {po_file.name}")
    print(f"{'='*70}")

    if not fr_file.exists():
        print(f"⚠️  No French source file found: {fr_file}")
        return 0

    # Load PO file
    po = polib.pofile(str(po_file))

    # Extract paragraphs from French file
    fr_paragraphs = extract_paragraphs(fr_file)
    print(f"📖 Found {len(fr_paragraphs)} French paragraphs")

    # Track statistics
    translated_count = 0
    skipped_count = 0

    # Process each entry in PO file
    for entry in po:
        if entry.msgid and not entry.msgstr:
            # Try to find matching French text
            match = find_best_match(entry.msgid, fr_paragraphs)

            if match:
                entry.msgstr = match
                translated_count += 1
                print(f"✓ Translated: {entry.msgid[:50]}...")
            else:
                skipped_count += 1
                print(f"⚠ No match: {entry.msgid[:50]}...")

    # Save PO file
    po.save()

    print(f"\n📊 Statistics:")
    print(f"   ✓ Translated: {translated_count}")
    print(f"   ⚠ Skipped: {skipped_count}")
    print(f"   📝 Total entries: {len(po)}")

    return translated_count


def main():
    """Main migration function."""
    print("\n" + "="*70)
    print("TRANSLATION MIGRATION TOOL")
    print("="*70)
    print("\nMigrating translations from docs/fr/ to locale/fr/LC_MESSAGES/\n")

    # Define paths
    locale_dir = Path("locale/fr/LC_MESSAGES")
    source_dir = Path("source")
    old_fr_dir = Path("fr")

    # Check directories exist
    if not locale_dir.exists():
        print(f"❌ Error: locale directory not found: {locale_dir}")
        return

    if not old_fr_dir.exists():
        print(f"❌ Error: old French docs not found: {old_fr_dir}")
        return

    # Get all PO files
    po_files = list(locale_dir.glob("*.po"))
    print(f"Found {len(po_files)} PO files to process\n")

    total_translated = 0

    # Process each PO file
    for po_file in sorted(po_files):
        # Get corresponding source files
        base_name = po_file.stem
        en_file = source_dir / f"{base_name}.md"
        fr_file = old_fr_dir / f"{base_name}.md"

        if not en_file.exists():
            print(f"⚠️  Skipping {po_file.name}: no English source found")
            continue

        translated = migrate_file(po_file, en_file, fr_file)
        total_translated += translated

    print("\n" + "="*70)
    print("MIGRATION COMPLETE")
    print("="*70)
    print(f"\n✓ Total translations migrated: {total_translated}")
    print("\n📝 Next steps:")
    print("   1. Review locale/fr/LC_MESSAGES/*.po files")
    print("   2. Manually translate any missing strings")
    print("   3. Run: make html-fr")
    print("   4. Test the French documentation")
    print()


if __name__ == "__main__":
    main()
