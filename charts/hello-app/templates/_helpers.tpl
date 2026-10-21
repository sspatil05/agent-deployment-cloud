{{- define "hello-app.name" -}}
{{- required "appName is required (set it in apps/<app>/values.yaml)" .Values.appName | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "hello-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "hello-app.name" . }}
{{- end -}}

{{- define "hello-app.labels" -}}
{{ include "hello-app.selectorLabels" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Values.image.tag | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version }}
{{- end -}}

{{- define "hello-app.image" -}}
{{- $repo := required "image.repository is required" .Values.image.repository -}}
{{- $tag := required "image.tag is required" .Values.image.tag -}}
{{- printf "%s:%s" $repo $tag -}}
{{- end -}}
