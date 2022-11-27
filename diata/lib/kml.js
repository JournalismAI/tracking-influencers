const fs = require('fs').promises;
const randomstring = require('randomstring');
const xmlescape = require('xml-escape');

function pair(options) {
	return `<Pair>
				<key>normal</key>
				<styleUrl>#__managed_style_${options.styleurl}</styleUrl>
			</Pair>`;
}

function cascadingstyle(options) {
	return `<gx:CascadingStyle kml:id="__managed_style_${options.styleurl}">
			<styleUrl>https://earth.google.com/balloon_components/base/1.0.23.0/card_template.kml#main</styleUrl>
			<Style>
				<IconStyle>
					<scale>1.2</scale>
					<Icon>
						<href>https://earth.google.com/earth/rpc/cc/icon?color=42a5f5&amp;id=2170&amp;scale=4</href>
					</Icon>
					<hotSpot x="64" y="128" xunits="pixels" yunits="insetPixels" />
				</IconStyle>
				<LabelStyle></LabelStyle>
				<LineStyle>
					<color>ff2dc0fb</color>
					<width>3</width>
				</LineStyle>
				<PolyStyle>
					<color>40ffffff</color>
				</PolyStyle>
				<BalloonStyle></BalloonStyle>
			</Style>
		</gx:CascadingStyle>`;
}

function placemark(options) {
	return `<Placemark id="${options.id}">
		<name>${xmlescape(options.name)}</name>
		<description>${xmlescape(options.description)}</description>
		<LookAt>
			<longitude>${options.longitude}</longitude>
			<latitude>${options.latitude}</latitude>
			<altitude>0</altitude>
			<heading>0</heading>
			<tilt>0</tilt>
			<gx:fovy>35</gx:fovy>
			<range>581.4836969875232</range>
			<altitudeMode>relativeToGround</altitudeMode>
		</LookAt>
		<styleUrl>#__managed_style_${options.styleurl}</styleUrl>
		<Point>
			<altitudeMode>relativeToGround</altitudeMode>
			<coordinates>${options.longitude},${options.latitude},0</coordinates>
		</Point>
	</Placemark>`;
}

async function generate(list, output) {

	const placemarks = list.map(item => {

		const id = randomstring.generate({
			length: 20,
			charset: 'alphabetic'
		}).toLocaleUpperCase();

		return placemark({
			id,
			longitude: item.lng,
			latitude: item.lat,
			styleurl: '0276783EEA1EFF0B3D00',
			name: item.id + ' C:' + item.commentsCount + ' L:' + ((item.likesCount > 0) ? item.likesCount : 0),
			description: item.url
		});

	});

	const cascadingstyles = [];

	const pairs = list.map(item => {

		const id = randomstring.generate({
			length: 20,
			charset: 'alphabetic'
		}).toLocaleUpperCase();

		cascadingstyles.push(cascadingstyle({
			styleurl: id
		}));

		return pair({
			styleurl: id
		});

	});

	const klm = `<?xml version="1.0" encoding="UTF-8"?><kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
        <Document>
		<name>Influencer</name>
        ${cascadingstyles.join('\n')}
        <StyleMap id="__managed_style_0276783EEA1EFF0B3D00">
			${pairs.join('\n')}
		</StyleMap>
        ${placemarks.join('\n')}
        </Document>
    </kml>`;

	await fs.writeFile(output, klm);

}

module.exports = {
	generate
};