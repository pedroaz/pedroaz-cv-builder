from pathlib import Path
from datetime import datetime


class CVGenerator:
    def __init__(self, template_name: str = "modern"):
        self.template_name = template_name
        template_dir = Path(__file__).parent / "templates"
        self.template_path = template_dir / f"{template_name}.html"

    def generate(self, data: dict) -> str:
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template '{self.template_name}' not found")

        with open(self.template_path) as f:
            template = f.read()

        html = self._render(template, data)
        return html

    def _render(self, template: str, data: dict) -> str:
        basics = data.get("basics", {})
        name = basics.get("name", "")
        label = basics.get("label", "")
        email = basics.get("email", "")
        phone = basics.get("phone", "")
        url = basics.get("url", "")
        summary = basics.get("summary", "")
        location = basics.get("location", {})
        image = basics.get("image", "")
        if image:
            image_path = Path(__file__).parent.parent / image
            image = f"file://{image_path.resolve()}"

        location_str = self._format_location(location)

        profiles_html = self._render_profiles(basics.get("profiles", []))

        work_html = self._render_work(data.get("work", []))
        education_html = self._render_education(data.get("education", []))
        skills_html = self._render_skills(data.get("skills", {}))
        other_experiences_html = self._render_other_experiences(data.get("otherExperiences", []))
        languages_html = self._render_languages(data.get("languages", []))
        awards_html = self._render_awards(data.get("awards", []))

        replacements = {
            "{{NAME}}": name,
            "{{LABEL}}": label,
            "{{LABEL_DISPLAY}}": f'<p class="label">{label}</p>' if label else '',
            "{{IMAGE_DISPLAY}}": f'<img src="{image}" class="profile-photo" alt="Profile photo">' if image else '',
            "{{EMAIL}}": email,
            "{{EMAIL_DISPLAY}}": f'<a href="mailto:{email}" class="contact-item">{email}</a>' if email else '',
            "{{PHONE}}": phone,
            "{{PHONE_DISPLAY}}": f'<a href="tel:{phone}" class="contact-item">{phone}</a>' if phone else '',
            "{{URL}}": url,
            "{{URL_DISPLAY}}": f'<a href="{url}" class="contact-item" target="_blank" rel="noopener noreferrer">{url}</a>' if url else '',
            "{{SUMMARY}}": summary,
            "{{SUMMARY_DISPLAY}}": f'<section class="summary-section"><p>{summary}</p></section>' if summary else '',
            "{{LOCATION}}": location_str,
            "{{LOCATION_DISPLAY}}": f'<span class="contact-item location">{location_str}</span>' if location_str else '',
            "{{PROFILES}}": profiles_html,
            "{{WORK}}": work_html,
            "{{EDUCATION}}": education_html,
            "{{SKILLS}}": skills_html,
            "{{OTHER_EXPERIENCES}}": other_experiences_html,
            "{{LANGUAGES}}": languages_html,
            "{{AWARDS}}": awards_html,
            "{{GENERATED_DATE}}": datetime.now().strftime("%Y-%m-%d"),
        }

        result = template
        for key, value in replacements.items():
            result = result.replace(key, value)

        return result

    def _format_location(self, location: dict) -> str:
        parts = []
        if location.get("city"):
            parts.append(location["city"])
        if location.get("region"):
            parts.append(location["region"])
        if location.get("countryCode"):
            parts.append(location["countryCode"])
        return ", ".join(parts)

    def _render_profiles(self, profiles: list) -> str:
        if not profiles:
            return ""
        html = '<div class="profiles">'
        for p in profiles:
            network = p.get("network", "")
            username = p.get("username", "")
            url = p.get("url", "")
            if url:
                html += f'<a href="{url}" class="profile-badge" target="_blank" rel="noopener noreferrer">{network}</a>'
            else:
                html += f'<span class="profile-badge">{network}: {username}</span>'
        html += '</div>'
        return html

    def _render_work(self, work_list: list) -> str:
        if not work_list:
            return ""
        html = '<section class="work"><h2>Experience</h2>'
        for w in work_list:
            name = w.get("name", "")
            start = self._format_date(w.get("startDate", ""))
            end = self._format_date(w.get("endDate", ""))
            date_str = f"{start} – {end}" if end else f"{start} – Present"
            summary = w.get("summary", "")
            highlights = w.get("highlights", [])
            positions = w.get("positions", [])
            skills = w.get("skills", [])
            skills_html = f'<div class="work-skills">{" • ".join(skills)}</div>' if skills else ""

            if positions:
                end_display = end if end else "Present"
                html += f'''
                <div class="work-entry">
                    <div class="company-header">
                        <span class="company-name">{name}</span>
                        <span class="company-tenure">({start} – {end_display})</span>
                    </div>
                    {skills_html}
                '''
                for pos in positions:
                    pos_start = self._format_date(pos.get("startDate", ""))
                    pos_end = self._format_date(pos.get("endDate", ""))
                    pos_date_str = f"{pos_start} – {pos_end}" if pos_end else f"{pos_start} – Present"
                    pos_title = pos.get("position", "")
                    pos_highlights = pos.get("highlights", [])

                    html += f'''
                    <div class="position-entry">
                        <span class="position-marker">●</span>
                        <span class="position-title">{pos_title}</span>
                        <span class="position-date">{pos_date_str}</span>
                    </div>
                    '''
                    if pos_highlights:
                        html += '<ul class="highlights">'
                        for h in pos_highlights:
                            html += f'<li>{h}</li>'
                        html += '</ul>'
                html += '</div>'
            else:
                position = w.get("position", "")
                end_display = end if end else "Present"
                position_html = f'''<div class="position-entry">
                        <span class="position-marker">&#9679;</span>
                        <span class="position-title">{position}</span>
                    </div>''' if position else ''
                html += f'''
                <div class="work-entry">
                    <div class="company-header">
                        <span class="company-name">{name}</span>
                        <span class="company-tenure">({start} – {end_display})</span>
                    </div>
                    {skills_html}
                    {position_html}
                '''
                if summary:
                    html += f'<p class="summary">{summary}</p>'
                if highlights:
                    html += '<ul class="highlights">'
                    for h in highlights:
                        html += f'<li>{h}</li>'
                    html += '</ul>'
                html += '</div>'
        html += '</section>'
        return html

    def _render_education(self, edu_list: list) -> str:
        if not edu_list:
            return ""
        html = '<section class="education"><h2>Education</h2>'
        for e in edu_list:
            institution = e.get("institution", "")
            area = e.get("area", "")
            study_type = e.get("studyType", "")
            start = self._format_date(e.get("startDate", ""))
            end = self._format_date(e.get("endDate", ""))
            date_str = f"{start} – {end}" if end else f"{start} – Present"
            score = e.get("score", "")
            url = e.get("url", "")

            title = f"{study_type} in {area}" if study_type and area else (study_type or area or institution)
            subtitle = institution
            if score:
                subtitle += f" | Score: {score}"
            if url:
                subtitle += f' <a href="{url}" target="_blank" rel="noopener noreferrer">🔗</a>'

            html += f'''
            <div class="entry">
                <div class="header">
                    <span class="title">{title}</span>
                    <span class="date">{date_str}</span>
                </div>
                <p class="subtitle">{subtitle}</p>
            </div>
            '''
        html += '</section>'
        return html

    def _render_skills(self, skills_dict: dict) -> str:
        if not skills_dict:
            return ""
        html = '<section class="skills"><h2>Skills</h2><div class="skills-inline">'
        parts = []
        for category, items in skills_dict.items():
            items_str = " • ".join(items) if isinstance(items, list) else items
            parts.append(f'<span class="skill-inline-item"><span class="skill-category">{category}:</span> <span class="skill-items">{items_str}</span></span>')
        html += ' <span class="skill-separator">|</span> '.join(parts)
        html += '</div></section>'
        return html

    def _render_projects(self, projects: list) -> str:
        if not projects:
            return ""
        html = '<section class="projects"><h2>Projects</h2>'
        for p in projects:
            name = p.get("name", "")
            description = p.get("description", "")
            start = self._format_date(p.get("startDate", ""))
            end = self._format_date(p.get("endDate", ""))
            date_str = f"{start} – {end}" if end else f"{start} – Present" if start else ""
            url = p.get("url", "")
            highlights = p.get("highlights", [])

            html += f'''
            <div class="entry">
                <div class="header">
                    <span class="title">{name}{f' <a href="{url}" target="_blank" rel="noopener noreferrer">🔗</a>' if url else ''}</span>
                    <span class="date">{date_str}</span>
                </div>
            '''
            if description:
                html += f'<p class="summary">{description}</p>'
            if highlights:
                html += '<ul class="highlights">'
                for h in highlights:
                    html += f'<li>{h}</li>'
                html += '</ul>'
            html += '</div>'
        html += '</section>'
        return html

    def _render_certificates(self, certs: list) -> str:
        if not certs:
            return ""
        html = '<section class="certificates"><h2>Certificates</h2><div class="cert-list">'
        for c in certs:
            name = c.get("name", "")
            issuer = c.get("issuer", "")
            date = self._format_date(c.get("date", ""))
            url = c.get("url", "")
            html += f'<div class="cert-item">{name}'
            if issuer:
                html += f' <span class="issuer">by {issuer}</span>'
            if date:
                html += f' <span class="date">({date})</span>'
            if url:
                html += f' <a href="{url}" target="_blank" rel="noopener noreferrer">🔗</a>'
            html += '</div>'
        html += '</div></section>'
        return html

    def _render_languages(self, langs: list) -> str:
        if not langs:
            return ""
        html = '<div class="header-languages">'
        for l in langs:
            lang = l.get("language", "")
            fluency = l.get("fluency", "")
            if "(" in fluency and ")" in fluency:
                fluency = fluency.split("(")[-1].split(")")[0]
            html += f'<span class="profile-badge">{lang}: {fluency}</span>'
        html += '</div>'
        return html

    def _render_awards(self, awards: list) -> str:
        if not awards:
            return ""
        html = '<section class="awards"><h2>Awards</h2>'
        for a in awards:
            title = a.get("title", "")
            date = self._format_date(a.get("date", ""))
            awarder = a.get("awarder", "")
            summary = a.get("summary", "")

            html += f'''
            <div class="entry">
                <div class="header">
                    <span class="title">{title}</span>
                    <span class="date">{date}</span>
                </div>
                {f'<p class="subtitle">{awarder}</p>' if awarder else ''}
                {f'<p class="summary">{summary}</p>' if summary else ''}
            </div>
            '''
        html += '</section>'
        return html

    def _render_other_experiences(self, experiences: list) -> str:
        if not experiences:
            return ""
        html = '<section class="other-experiences"><h2>Other Experiences</h2><div class="other-exp-grid">'
        for e in experiences:
            title = e.get("title", "")
            description = e.get("description", "")

            html += f'''
            <div class="other-exp-item">
                <div class="position-entry">
                    <span class="position-marker">●</span>
                    <span class="position-title">{title}</span>
                </div>
                {f'<p class="other-exp-desc">{description}</p>' if description else ''}
            </div>
            '''
        html += '</div></section>'
        return html

    def _format_date(self, date_str: str) -> str:
        if not date_str:
            return ""
        parts = date_str.split("-")
        if len(parts) == 3:
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            try:
                return f"{months[int(parts[1]) - 1]} {parts[0]}"
            except (ValueError, IndexError):
                return date_str
        elif len(parts) == 2:
            try:
                months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                return f"{months[int(parts[1]) - 1]} {parts[0]}"
            except (ValueError, IndexError):
                return date_str
        return date_str
